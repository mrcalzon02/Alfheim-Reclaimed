package com.continuityworks.alfheimcompanion.worker;

import com.github.tjake.jlama.model.AbstractModel;
import com.github.tjake.jlama.model.ModelSupport;
import com.github.tjake.jlama.safetensors.DType;
import com.github.tjake.jlama.safetensors.prompt.PromptContext;
import com.github.tjake.jlama.util.Downloader;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.IOError;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicLong;

/** Loopback-only, single-request Jlama host for the Java 17 Forge client. */
public final class WorkerMain {
    private static final int MAX_REQUEST_BYTES = 16 * 1024;

    private WorkerMain() {}

    public static void main(String[] args) throws Exception {
        Arguments options = Arguments.parse(args);
        if (options.download()) {
            File downloaded = new Downloader(options.modelsRoot().toString(), options.modelId())
                    .huggingFaceModel();
            System.out.println(downloaded.getAbsolutePath());
            return;
        }

        Path modelDirectory = options.modelDirectory();
        if (!Files.isDirectory(modelDirectory))
            throw new IllegalArgumentException("Model directory does not exist: " + modelDirectory);
        System.out.println("Loading " + options.modelId() + " from " + modelDirectory);
        AbstractModel model = ModelSupport.loadModel(modelDirectory.toFile(), DType.F32, DType.I8);
        AtomicLong lastRequest = new AtomicLong(System.currentTimeMillis());
        HttpServer server = HttpServer.create(new InetSocketAddress(
                InetAddress.getByName("127.0.0.1"), options.port()), 0);
        server.setExecutor(Executors.newSingleThreadExecutor(runnable -> {
            Thread thread = new Thread(runnable, "alfheim-inference");
            thread.setDaemon(false);
            return thread;
        }));
        server.createContext("/health", exchange -> respond(exchange, 200,
                "{\"status\":\"ready\",\"model\":\"" + escape(options.modelId()) + "\"}"));
        server.createContext("/v1/chat/completions", exchange -> {
            lastRequest.set(System.currentTimeMillis());
            handleCompletion(exchange, model, options);
        });
        server.start();
        System.out.println("READY http://127.0.0.1:" + options.port());

        if (options.idleSeconds() > 0) {
            Thread.ofPlatform().name("alfheim-inference-idle-watch").start(() -> {
                while (true) {
                    try { Thread.sleep(5_000L); }
                    catch (InterruptedException interrupted) { return; }
                    if (System.currentTimeMillis() - lastRequest.get() > options.idleSeconds() * 1000L) {
                        System.out.println("Stopping after idle timeout");
                        server.stop(1);
                        try { model.close(); } catch (Exception ignored) {}
                        return;
                    }
                }
            });
        }
    }

    private static void handleCompletion(HttpExchange exchange, AbstractModel model, Arguments options)
            throws IOException {
        if (!"POST".equalsIgnoreCase(exchange.getRequestMethod())) {
            respond(exchange, 405, "{\"error\":\"POST required\"}");
            return;
        }
        try {
            JsonObject body = readObject(exchange.getRequestBody());
            JsonArray messages = body.getAsJsonArray("messages");
            if (messages == null || messages.isEmpty()) throw new IllegalArgumentException("messages required");
            String system = "";
            String user = "";
            for (var element : messages) {
                JsonObject message = element.getAsJsonObject();
                String role = message.get("role").getAsString();
                String content = message.get("content").getAsString();
                if ("system".equals(role)) system = content;
                if ("user".equals(role)) user = content;
            }
            if (user.isBlank()) throw new IllegalArgumentException("user message required");
            int tokens = body.has("max_tokens") ? body.get("max_tokens").getAsInt() : 64;
            tokens = Math.max(16, Math.min(64, tokens));
            PromptContext prompt;
            if (model.promptSupport().isPresent()) {
                prompt = model.promptSupport().get().builder()
                        .addSystemMessage(system).addUserMessage(user).build();
            } else {
                prompt = PromptContext.of(system + "\n\n" + user);
            }
            int promptTokens = model.encodePrompt(prompt).length;
            if (promptTokens > 448) throw new IllegalArgumentException("prompt exceeds 448-token evidence budget");
            int totalTokens = Math.min(512, promptTokens + tokens);
            var generated = model.generate(UUID.randomUUID(), prompt, 0.0F, totalTokens, (text, timing) -> {});

            JsonObject message = new JsonObject();
            message.addProperty("role", "assistant");
            message.addProperty("content", generated.responseText);
            JsonObject choice = new JsonObject();
            choice.addProperty("index", 0);
            choice.add("message", message);
            JsonArray choices = new JsonArray();
            choices.add(choice);
            JsonObject response = new JsonObject();
            response.addProperty("id", "alfheim-" + UUID.randomUUID());
            response.addProperty("created", Instant.now().getEpochSecond());
            response.addProperty("model", options.modelId());
            response.add("choices", choices);
            respond(exchange, 200, response.toString());
        } catch (IllegalArgumentException error) {
            respond(exchange, 400, error(error.getMessage()));
        } catch (RuntimeException | IOError error) {
            error.printStackTrace(System.err);
            respond(exchange, 500, error("generation failed"));
        }
    }

    private static JsonObject readObject(InputStream input) throws IOException {
        byte[] bytes = input.readNBytes(MAX_REQUEST_BYTES + 1);
        if (bytes.length > MAX_REQUEST_BYTES) throw new IllegalArgumentException("request too large");
        return JsonParser.parseString(new String(bytes, StandardCharsets.UTF_8)).getAsJsonObject();
    }

    private static void respond(HttpExchange exchange, int status, String json) throws IOException {
        byte[] bytes = json.getBytes(StandardCharsets.UTF_8);
        exchange.getResponseHeaders().set("Content-Type", "application/json; charset=utf-8");
        exchange.sendResponseHeaders(status, bytes.length);
        exchange.getResponseBody().write(bytes);
        exchange.close();
    }

    private static String error(String message) {
        JsonObject object = new JsonObject();
        object.addProperty("error", message == null ? "invalid request" : message);
        return object.toString();
    }

    private static String escape(String value) {
        return value.replace("\\", "\\\\").replace("\"", "\\\"");
    }

    private record Arguments(String modelId, Path modelsRoot, Path modelDirectory,
                             int port, int idleSeconds, boolean download) {
        private static Arguments parse(String[] args) {
            String model = "tjake/Qwen2.5-0.5B-Instruct-JQ4";
            Path root = Path.of("models").toAbsolutePath().normalize();
            Path directory = null;
            int port = 18081;
            int idle = 900;
            boolean download = false;
            List<String> values = List.of(args);
            for (int index = 0; index < values.size(); index++) {
                switch (values.get(index)) {
                    case "--model" -> model = required(values, ++index, "--model");
                    case "--models-root" -> root = Path.of(required(values, ++index, "--models-root"))
                            .toAbsolutePath().normalize();
                    case "--model-dir" -> directory = Path.of(required(values, ++index, "--model-dir"))
                            .toAbsolutePath().normalize();
                    case "--port" -> port = Integer.parseInt(required(values, ++index, "--port"));
                    case "--idle-seconds" -> idle = Integer.parseInt(required(values, ++index, "--idle-seconds"));
                    case "--download" -> download = true;
                    default -> throw new IllegalArgumentException("Unknown argument: " + values.get(index));
                }
            }
            if (port < 1024 || port > 65535) throw new IllegalArgumentException("port out of range");
            if (idle < 0 || idle > 86_400) throw new IllegalArgumentException("idle timeout out of range");
            if (directory == null) directory = root.resolve(model.replace('/', '_'));
            return new Arguments(model, root, directory, port, idle, download);
        }

        private static String required(List<String> args, int index, String option) {
            if (index >= args.size()) throw new IllegalArgumentException(option + " requires a value");
            return args.get(index);
        }
    }
}

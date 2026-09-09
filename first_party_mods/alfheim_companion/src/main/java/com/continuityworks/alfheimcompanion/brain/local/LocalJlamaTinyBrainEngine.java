package com.continuityworks.alfheimcompanion.brain.local;

import com.continuityworks.alfheimcompanion.brain.AmbientSnapshot;
import com.continuityworks.alfheimcompanion.brain.BrainDecision;
import com.continuityworks.alfheimcompanion.brain.BrainSnapshot;
import com.continuityworks.alfheimcompanion.brain.TinyBrainEngine;
import com.continuityworks.alfheimcompanion.brain.ClaimDistrictDecision;
import com.continuityworks.alfheimcompanion.brain.ClaimDistrictSnapshot;
import com.continuityworks.alfheimcompanion.brain.AutonomousActivityDecision;
import com.continuityworks.alfheimcompanion.brain.AutonomousActivitySnapshot;
import com.continuityworks.alfheimcompanion.conversation.DeterministicConversationRouter;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.net.URI;
import java.io.IOException;
import java.util.Optional;
import java.util.concurrent.CompletableFuture;

/** Java 17 client for the separately hosted Java 21 Jlama worker. */
public final class LocalJlamaTinyBrainEngine implements TinyBrainEngine {
    private final InferenceSettings settings;
    private final HttpClient client;
    private final WorkerProcessManager worker;

    public LocalJlamaTinyBrainEngine(InferenceSettings settings) {
        this.settings = settings;
        this.client = HttpClient.newBuilder().connectTimeout(settings.timeout()).build();
        this.worker = new WorkerProcessManager(settings);
    }

    @Override
    public String engineId() {
        return "jlama-loopback:" + settings.model();
    }

    @Override public void activate() { worker.activate(); }

    @Override public void deactivate() { worker.deactivate(); }

    @Override
    public CompletableFuture<BrainDecision> plan(BrainSnapshot snapshot) {
        Optional<BrainDecision> catalogDecision = DeterministicConversationRouter.route(snapshot);
        if (catalogDecision.isPresent()) return CompletableFuture.completedFuture(catalogDecision.get());
        activate();
        JsonObject requestBody = new JsonObject();
        requestBody.addProperty("model", settings.model());
        requestBody.addProperty("temperature", 0.0D);
        requestBody.addProperty("max_tokens", settings.maxOutputTokens());
        requestBody.addProperty("stream", false);
        JsonArray messages = new JsonArray();
        messages.add(message("system", InferencePrompt.system(settings.allowFreeform())));
        messages.add(message("user", InferencePrompt.user(snapshot, settings.allowFreeform())));
        requestBody.add("messages", messages);

        HttpRequest request = HttpRequest.newBuilder(settings.endpoint())
                .timeout(settings.timeout())
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(requestBody.toString()))
                .build();
        return awaitReady().thenCompose(ignored -> client.sendAsync(request, HttpResponse.BodyHandlers.ofString()))
                .thenApply(response -> {
                    if (response.statusCode() < 200 || response.statusCode() >= 300)
                        throw new IllegalStateException("local inference worker returned HTTP " + response.statusCode());
                    return InferenceResponseParser.parse(completionText(response.body()), snapshot,
                            settings.allowFreeform());
                });
    }

    @Override
    public CompletableFuture<ClaimDistrictDecision> chooseClaimDistrict(ClaimDistrictSnapshot snapshot) {
        activate();
        String system = "Choose whether to keep or relocate one Minecraft claim district. Return one JSON object only: "
                + "{\"directive\":\"ADVISE\",\"target\":0,\"choice\":\"KEEP_DISTRICT\"}. "
                + "choice must be KEEP_DISTRICT or RELOCATE_DISTRICT. Prefer KEEP when values differ by less than 10.";
        String user = "preset=" + snapshot.behaviorPreset() + "\ncurrent_value=" + snapshot.currentValue()
                + "\ncurrent_reasons=" + snapshot.currentReasons() + "\ncandidate_value="
                + snapshot.candidateValue() + "\ncandidate_reasons=" + snapshot.candidateReasons();
        return completion(system, user).thenApply(output -> {
            JsonObject json = boundedObject(output);
            ClaimDistrictDecision.Choice choice;
            try { choice = ClaimDistrictDecision.Choice.valueOf(json.get("choice").getAsString()); }
            catch (RuntimeException error) { throw new IllegalArgumentException("invalid claim district choice", error); }
            return new ClaimDistrictDecision(snapshot.requestId(), choice);
        });
    }

    @Override
    public CompletableFuture<AutonomousActivityDecision> chooseAutonomousActivity(
            AutonomousActivitySnapshot snapshot) {
        activate();
        String system = "Choose one offered Minecraft companion activity. Return one JSON object only: "
                + "{\"choice\":\"OFFERED_ID\"}. Never invent an ID, coordinate, item, block, or action.";
        String user = "preset=" + snapshot.behaviorPreset() + "\nneeds=" + snapshot.nutrition()
                + "/20," + snapshot.stamina() + "/100\nclaims=" + snapshot.claimCount()
                + "\nprevious=" + snapshot.previousChoice() + "\noptions="
                + snapshot.options().stream().map(option -> option.id() + ":" + option.value()
                        + ":" + option.reason()).toList();
        return completion(system, user).thenApply(output -> {
            JsonObject json = boundedObject(output);
            String choice;
            try { choice = json.get("choice").getAsString(); }
            catch (RuntimeException error) {
                throw new IllegalArgumentException("missing autonomous activity choice", error);
            }
            if (!snapshot.offers(choice))
                throw new IllegalArgumentException("model selected an unoffered autonomous activity");
            return new AutonomousActivityDecision(snapshot.requestId(), choice);
        });
    }

    private CompletableFuture<Void> awaitReady() {
        return CompletableFuture.runAsync(() -> {
            long deadline = System.nanoTime() + settings.timeout().toNanos();
            URI endpoint = settings.endpoint();
            URI health = URI.create("http://" + endpoint.getHost() + ":" + endpoint.getPort() + "/health");
            HttpRequest request = HttpRequest.newBuilder(health).timeout(settings.timeout()).GET().build();
            Throwable last = null;
            while (System.nanoTime() < deadline) {
                try {
                    HttpResponse<Void> response = client.send(request, HttpResponse.BodyHandlers.discarding());
                    if (response.statusCode() == 200) return;
                    last = new IllegalStateException("health check returned HTTP " + response.statusCode());
                } catch (IOException error) {
                    last = error;
                } catch (InterruptedException interrupted) {
                    Thread.currentThread().interrupt();
                    throw new IllegalStateException("interrupted while waiting for local inference", interrupted);
                }
                try { Thread.sleep(150L); }
                catch (InterruptedException interrupted) {
                    Thread.currentThread().interrupt();
                    throw new IllegalStateException("interrupted while waiting for local inference", interrupted);
                }
            }
            throw new IllegalStateException("local inference worker did not become ready", last);
        });
    }

    private CompletableFuture<String> completion(String system, String user) {
        JsonObject requestBody = new JsonObject();
        requestBody.addProperty("model", settings.model());
        requestBody.addProperty("temperature", 0.0D);
        requestBody.addProperty("max_tokens", Math.min(48, settings.maxOutputTokens()));
        requestBody.addProperty("stream", false);
        JsonArray messages = new JsonArray();
        messages.add(message("system", system));
        messages.add(message("user", user));
        requestBody.add("messages", messages);
        HttpRequest request = HttpRequest.newBuilder(settings.endpoint()).timeout(settings.timeout())
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(requestBody.toString())).build();
        return awaitReady().thenCompose(ignored -> client.sendAsync(request, HttpResponse.BodyHandlers.ofString()))
                .thenApply(response -> {
                    if (response.statusCode() < 200 || response.statusCode() >= 300)
                        throw new IllegalStateException("local inference worker returned HTTP " + response.statusCode());
                    return completionText(response.body());
                });
    }

    private static JsonObject boundedObject(String output) {
        if (output == null) throw new IllegalArgumentException("empty model output");
        int start = output.indexOf('{');
        int end = output.lastIndexOf('}');
        if (start < 0 || end < start) throw new IllegalArgumentException("model output is not JSON");
        return JsonParser.parseString(output.substring(start, end + 1)).getAsJsonObject();
    }

    /** Ambient speech remains catalog-driven; the model is not spent on routine travel chatter. */
    @Override
    public CompletableFuture<Optional<String>> reflect(AmbientSnapshot snapshot) {
        return CompletableFuture.completedFuture(Optional.empty());
    }

    private static JsonObject message(String role, String content) {
        JsonObject message = new JsonObject();
        message.addProperty("role", role);
        message.addProperty("content", content);
        return message;
    }

    static String completionText(String body) {
        JsonObject root = JsonParser.parseString(body).getAsJsonObject();
        JsonArray choices = root.getAsJsonArray("choices");
        if (choices == null || choices.isEmpty()) throw new IllegalArgumentException("worker returned no choices");
        JsonObject first = choices.get(0).getAsJsonObject();
        if (first.has("message")) return first.getAsJsonObject("message").get("content").getAsString();
        if (first.has("text")) return first.get("text").getAsString();
        throw new IllegalArgumentException("worker response has no completion text");
    }
}

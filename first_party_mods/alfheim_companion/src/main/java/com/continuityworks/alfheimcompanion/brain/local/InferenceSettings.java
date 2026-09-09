package com.continuityworks.alfheimcompanion.brain.local;

import java.io.IOException;
import java.io.Reader;
import java.net.URI;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.Locale;
import java.util.Properties;

/** User-controlled connection settings for the loopback-only inference worker. */
public record InferenceSettings(
        boolean enabled,
        URI endpoint,
        String model,
        Duration timeout,
        int maxOutputTokens,
        boolean allowFreeform,
        boolean manageWorker,
        Path javaExecutable,
        Path workerDirectory,
        Path modelDirectory,
        int idleSeconds
) {
    public static final String FILE_NAME = "alfheim_companion-inference.properties";
    public static final URI DEFAULT_ENDPOINT = URI.create("http://127.0.0.1:18081/v1/chat/completions");
    public static final String DEFAULT_MODEL = "tjake/Qwen2.5-0.5B-Instruct-JQ4";

    public InferenceSettings {
        endpoint = requireLoopback(endpoint);
        model = bounded(model, 120);
        timeout = timeout == null ? Duration.ofSeconds(12) : timeout;
        if (timeout.isNegative() || timeout.isZero() || timeout.compareTo(Duration.ofSeconds(30)) > 0)
            throw new IllegalArgumentException("timeout must be within 1..30 seconds");
        maxOutputTokens = Math.max(16, Math.min(64, maxOutputTokens));
        idleSeconds = Math.max(60, Math.min(3600, idleSeconds));
    }

    public static InferenceSettings load(Path configDirectory, Path gameDirectory) throws IOException {
        Path file = configDirectory.resolve(FILE_NAME);
        if (!Files.isRegularFile(file)) return defaults(false, gameDirectory);
        Properties properties = new Properties();
        try (Reader reader = Files.newBufferedReader(file)) {
            properties.load(reader);
        }
        return from(properties, gameDirectory);
    }

    static InferenceSettings from(Properties properties, Path gameDirectory) {
        boolean enabled = Boolean.parseBoolean(properties.getProperty("enabled", "false"));
        URI endpoint = URI.create(properties.getProperty("endpoint", DEFAULT_ENDPOINT.toString()).strip());
        String model = properties.getProperty("model", DEFAULT_MODEL);
        int timeout = integer(properties, "timeout_seconds", 12, 1, 30);
        int tokens = integer(properties, "max_output_tokens", 64, 16, 64);
        boolean freeform = Boolean.parseBoolean(properties.getProperty("allow_freeform", "false"));
        boolean manage = Boolean.parseBoolean(properties.getProperty("manage_worker", "true"));
        Path java = inside(gameDirectory, properties.getProperty("java_path",
                "alfheim_companion/inference/runtime/bin/java.exe"));
        Path worker = inside(gameDirectory, properties.getProperty("worker_directory",
                "alfheim_companion/inference/worker"));
        Path modelDirectory = inside(gameDirectory, properties.getProperty("model_directory",
                "alfheim_companion/inference/models/" + model.replace('/', '_')));
        int idle = integer(properties, "idle_seconds", 300, 60, 3600);
        return new InferenceSettings(enabled, endpoint, model, Duration.ofSeconds(timeout), tokens, freeform,
                manage, java, worker, modelDirectory, idle);
    }

    public static InferenceSettings defaults(boolean enabled, Path gameDirectory) {
        Path root = gameDirectory.toAbsolutePath().normalize();
        return new InferenceSettings(enabled, DEFAULT_ENDPOINT, DEFAULT_MODEL,
                Duration.ofSeconds(12), 64, false, true,
                root.resolve("alfheim_companion/inference/runtime/bin/java.exe"),
                root.resolve("alfheim_companion/inference/worker"),
                root.resolve("alfheim_companion/inference/models/" + DEFAULT_MODEL.replace('/', '_')), 300);
    }

    private static URI requireLoopback(URI value) {
        if (value == null || !"http".equalsIgnoreCase(value.getScheme()))
            throw new IllegalArgumentException("inference endpoint must use plain HTTP on loopback");
        String host = value.getHost();
        if (host == null) throw new IllegalArgumentException("inference endpoint has no host");
        String normalized = host.toLowerCase(Locale.ROOT);
        if (!(normalized.equals("127.0.0.1") || normalized.equals("localhost")
                || normalized.equals("::1") || normalized.equals("[::1]"))) {
            throw new IllegalArgumentException("inference endpoint must be loopback-only");
        }
        return value;
    }

    private static int integer(Properties properties, String key, int fallback, int minimum, int maximum) {
        try {
            int value = Integer.parseInt(properties.getProperty(key, String.valueOf(fallback)).strip());
            return Math.max(minimum, Math.min(maximum, value));
        } catch (NumberFormatException ignored) {
            return fallback;
        }
    }

    private static String bounded(String value, int maximum) {
        if (value == null || value.isBlank()) return DEFAULT_MODEL;
        String clean = value.strip();
        return clean.length() <= maximum ? clean : clean.substring(0, maximum);
    }

    private static Path inside(Path gameDirectory, String configured) {
        Path root = gameDirectory.toAbsolutePath().normalize();
        Path resolved = root.resolve(configured).toAbsolutePath().normalize();
        if (!resolved.startsWith(root))
            throw new IllegalArgumentException("inference runtime paths must remain inside the game directory");
        return resolved;
    }
}

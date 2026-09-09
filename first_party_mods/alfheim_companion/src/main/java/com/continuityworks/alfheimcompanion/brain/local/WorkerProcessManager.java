package com.continuityworks.alfheimcompanion.brain.local;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;

/** Starts and stops only the packaged worker and model paths validated by {@link InferenceSettings}. */
final class WorkerProcessManager implements AutoCloseable {
    private static final String MAIN_CLASS = "com.continuityworks.alfheimcompanion.worker.WorkerMain";
    private final InferenceSettings settings;
    private Process process;

    WorkerProcessManager(InferenceSettings settings) {
        this.settings = settings;
    }

    synchronized void activate() {
        if (!settings.manageWorker() || (process != null && process.isAlive())) return;
        Path java = settings.javaExecutable();
        Path libraries = settings.workerDirectory().resolve("lib");
        Path temporary = settings.workerDirectory().resolve("tmp");
        if (!Files.isRegularFile(java)) throw new IllegalStateException("Java 21 runtime is not installed: " + java);
        if (!Files.isDirectory(libraries)) throw new IllegalStateException("Inference worker is not installed: " + libraries);
        if (!Files.isDirectory(settings.modelDirectory()))
            throw new IllegalStateException("Inference model is not installed: " + settings.modelDirectory());

        List<String> command = new ArrayList<>();
        command.add(java.toString());
        command.add("--enable-preview");
        command.add("--add-modules=jdk.incubator.vector");
        command.add("--enable-native-access=ALL-UNNAMED");
        command.add("-Djava.io.tmpdir=" + temporary);
        command.add("-Xms128m");
        command.add("-Xmx512m");
        command.add("-cp");
        command.add(libraries.resolve("*").toString());
        command.add(MAIN_CLASS);
        command.add("--model");
        command.add(settings.model());
        command.add("--model-dir");
        command.add(settings.modelDirectory().toString());
        command.add("--port");
        command.add(String.valueOf(settings.endpoint().getPort()));
        command.add("--idle-seconds");
        command.add(String.valueOf(settings.idleSeconds()));
        try {
            Files.createDirectories(settings.workerDirectory());
            Files.createDirectories(temporary);
            process = new ProcessBuilder(command)
                    .directory(settings.workerDirectory().toFile())
                    .redirectErrorStream(true)
                    .redirectOutput(ProcessBuilder.Redirect.appendTo(
                            settings.workerDirectory().resolve("worker.log").toFile()))
                    .start();
        } catch (IOException error) {
            throw new IllegalStateException("Could not start local inference worker", error);
        }
    }

    synchronized void deactivate() {
        if (process == null) return;
        process.destroy();
        try {
            if (!process.waitFor(2, TimeUnit.SECONDS)) process.destroyForcibly();
        } catch (InterruptedException interrupted) {
            Thread.currentThread().interrupt();
            process.destroyForcibly();
        } finally {
            process = null;
        }
    }

    @Override public void close() { deactivate(); }
}

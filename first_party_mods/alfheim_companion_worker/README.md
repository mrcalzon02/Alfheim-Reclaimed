# Alfheim Companion inference worker

This Java 21 process hosts `tjake/Qwen2.5-0.5B-Instruct-JQ4` for the Java 17 Forge mod. It binds only
to `127.0.0.1`, serializes all generation through one thread, forces temperature zero, caps output at
64 tokens and the whole context at 512 tokens, caps the Java heap at 512 MiB, rejects requests over
16 KiB, and unloads the model after an idle timeout.

Use the companion Gradle wrapper from this directory:

```powershell
..\alfheim_companion\gradlew.bat -p . installDist
..\alfheim_companion\gradlew.bat -p . run --args="--download --models-root ..\..\alfheim_companion\inference\models"
```

Model download is explicit; normal game startup never downloads model files. The Forge-side client
falls back to its deterministic rule engine when this worker is absent, loading, malformed, or late.

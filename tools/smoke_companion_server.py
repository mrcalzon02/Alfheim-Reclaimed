#!/usr/bin/env python3
"""Bounded, non-mutating Forge dedicated-server smoke test of a verified candidate.

Stages ONLY in an OS temporary directory. The tracked pack, jars, worlds and
configs are never modified. No third-party jars are packaged as test artifacts.
This is minimal Forge+companion boot validation, NOT full modpack/multiplayer
acceptance.

python3 tools/smoke_companion_server.py --self-test
python3 tools/smoke_companion_server.py --server-root smoke-source/server \
    --candidate smoke-candidate/alfheim_companion-0.2.0.jar \
    --expected-sha256 f88b8bbd746631cdbf9fb23575d335cfbe97259dde913d5840d55656cf7eb246 \
    --output-dir smoke-evidence
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time

ARGFILE = Path("libraries/net/minecraftforge/forge/1.20.1-47.4.10/unix_args.txt")
JAR_NAME = "alfheim_companion-0.2.0.jar"
READY = re.compile(r'Done \([0-9.]+s\)! For help, type "help"')
MAX_LOG_BYTES = 2_000_000


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def eula_accepted(content):
    return any(re.fullmatch(r"\s*eula\s*=\s*true\s*", line, re.IGNORECASE)
               for line in content.splitlines())


def read_log(path):
    return Path(path).read_text(encoding="utf-8", errors="replace") if Path(path).exists() else ""


def self_test():
    assert eula_accepted("# approved by owner\neula=true\n")
    assert eula_accepted("EULA = TRUE\n")
    assert not eula_accepted("# eula=true\neula=false\n")
    assert not eula_accepted("eula=FALSE\n")
    assert READY.search('[Server thread/INFO]: Done (31.48s)! For help, type "help"')
    assert not READY.search('Server is still loading; no Done message')
    assert command_outputs_seen("Companion profiles: Liria\nCompanion outfits: wayfinder")
    assert not command_outputs_seen("Done (31.48s)! For help, type \"help\"")
    with tempfile.TemporaryDirectory(prefix="alfheim-smoke-selftest-") as temp:
        jar = Path(temp) / JAR_NAME
        jar.write_bytes(b"first-party-candidate-fixture")
        observed = sha256(jar)
        assert len(observed) == 64
        assert observed == hashlib.sha256(jar.read_bytes()).hexdigest()
        assert observed != sha256(Path(__file__))
    print("COMPANION_SERVER_SMOKE_PREFLIGHT_PASS: EULA, readiness, hash and bounded-stage checks")


def command_outputs_seen(messages):
    # Actual server command responses, not the command text itself.
    return "Companion profiles:" in messages and "Companion outfits:" in messages


def stop_process(process):
    if process is None or process.poll() is not None:
        return
    try:
        process.terminate()
        process.wait(timeout=15)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=15)


def boot(stage, output, heap_gib, timeout):
    log = output / "server-console.log"
    command = ["java", "-Xms512M", f"-Xmx{heap_gib}G", "-Djava.awt.headless=true",
               f"@{ARGFILE.as_posix()}", "nogui"]
    report = {"command": command, "ready": False, "clean_exit": False,
              "exit_code": None, "duration_seconds": None}
    process = None
    start = time.monotonic()
    try:
        with log.open("w", encoding="utf-8", errors="replace") as log_stream:
            process = subprocess.Popen(
                command, cwd=stage, stdin=subprocess.PIPE,
                stdout=log_stream, stderr=subprocess.STDOUT,
                text=True, bufsize=1)
            deadline = start + timeout
            while time.monotonic() < deadline:
                time.sleep(2)
                messages = read_log(log)
                if READY.search(messages):
                    report["ready"] = True
                    if process.poll() is not None:
                        break
                    # Prove that the companion mod registered its real player-facing
                    # commands. Mere Forge readiness would not establish mod loading.
                    for command_line in ("alfheimcompanion profile list",
                                         "alfheimcompanion outfit list", "list"):
                        process.stdin.write(command_line + "\n")
                        process.stdin.flush()
                        time.sleep(1)
                    process.stdin.write("stop\n")
                    process.stdin.flush()
                    try:
                        process.wait(timeout=60)
                    except subprocess.TimeoutExpired:
                        report["error"] = "Server did not stop after console command"
                    break
                if process.poll() is not None:
                    report["error"] = "JVM terminated before server readiness"
                    break
            else:
                report["error"] = "Server did not reach ready state before timeout"
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        report["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        stop_process(process)
        report["duration_seconds"] = round(time.monotonic() - start, 1)
        report["exit_code"] = None if process is None else process.returncode
        report["clean_exit"] = report["ready"] and report["exit_code"] == 0
        final = read_log(log)
        report["companion_id_in_log"] = "alfheim_companion" in final.lower()
        report["companion_profile_command_ok"] = "Companion profiles:" in final
        report["companion_outfit_command_ok"] = "Companion outfits:" in final
        if report["ready"] and report["exit_code"] == 0 and not command_outputs_seen(final):
            report["error"] = "Forge booted, but companion profile/outfit command replies were missing"
        report["clean_exit"] = report["clean_exit"] and command_outputs_seen(final)
        report["last_log_lines"] = final.splitlines()[-35:]
        # Keep useful evidence bounded; upload no source jars or player/world files.
        if len(final.encode("utf-8")) > MAX_LOG_BYTES:
            log.write_text(final[-MAX_LOG_BYTES:], encoding="utf-8")
    return report


def smoke_test(args):
    output = Path(args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    report = {
        "profile": "minimal-forge-companion-dedicated-server",
        "admission": "startup-smoke-only; not full pack, save, client or multiplayer",
        "expected_candidate_sha256": args.expected_sha256,
        "source_commit": "f1a43100c45ba1efb52db673f624362774fa6f4f",
        "candidate_artifact_id": 14580075904,
        "candidate_build_run_id": 44626195977,
        "heap_gib": args.heap_gib,
        "timeout_seconds": args.timeout,
        "success": False
    }
    try:
        candidate = Path(args.candidate).resolve()
        server = Path(args.server_root).resolve()
        if not candidate.is_file():
            raise ValueError(f"Candidate JAR missing: {candidate}")
        actual = sha256(candidate)
        report["candidate_sha256"] = actual
        if actual != args.expected_sha256.lower():
            raise ValueError("Candidate SHA-256 differs from recorded successful Forge build")
        if not (server / ARGFILE).is_file():
            raise ValueError(f"Forge server argfile absent in staging source: {ARGFILE}")
        eula = server / "eula.txt"
        if not eula.is_file() or not eula_accepted(eula.read_text(encoding="utf-8")):
            raise ValueError("Owner-accepted EULA file missing; cannot stage a server")

        with tempfile.TemporaryDirectory(prefix="alfheim-companion-forge-smoke-") as temp:
            stage = Path(temp) / "server"
            stage.mkdir()
            shutil.copytree(server / "libraries", stage / "libraries")
            shutil.copy2(eula, stage / "eula.txt")
            mods = stage / "mods"
            mods.mkdir()
            shutil.copy2(candidate, mods / JAR_NAME)
            client = Path(temp) / "client-mods"
            client.mkdir()
            shutil.copy2(candidate, client / JAR_NAME)
            hashes = [sha256(mods / JAR_NAME), sha256(client / JAR_NAME)]
            report["staged_server_sha256"] = hashes[0]
            report["staged_client_copy_sha256"] = hashes[1]
            if hashes != [actual, actual]:
                raise ValueError("Staging copies differ from verified candidate")

            # Bind to loopback: this validation server must never become public.
            (stage / "server.properties").write_text(
                "level-name=ci-alfheim-companion-smoke\n"
                "server-ip=127.0.0.1\n"
                "server-port=25565\n"
                "online-mode=false\n"
                "enforce-secure-profile=false\n"
                "max-players=2\n"
                "view-distance=4\n"
                "simulation-distance=4\n"
                "spawn-protection=0\n"
                "max-tick-time=-1\n"
                "gamemode=creative\n"
                "motd=Alfheim first-party candidate CI smoke\n",
                encoding="utf-8")
            result = boot(stage, output, args.heap_gib, args.timeout)
            report.update(result)
            report["success"] = result["ready"] and result["clean_exit"]
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        report["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        (output / "smoke-report.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if report["success"]:
        print("COMPANION_SERVER_SMOKE_PASS: exact SHA-256, minimal Forge ready, companion profile/outfit commands and clean stop")
        return 0
    print("COMPANION_SERVER_SMOKE_FAIL: " + str(report.get("error", report.get("last_log_lines", [])[-5:])))
    return 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--server-root", default="smoke-source/server")
    parser.add_argument("--candidate", default=f"smoke-candidate/{JAR_NAME}")
    parser.add_argument("--expected-sha256",
                        default="f88b8bbd746631cdbf9fb23575d335cfbe97259dde913d5840d55656cf7eb246")
    parser.add_argument("--output-dir", default="smoke-evidence")
    parser.add_argument("--heap-gib", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=480)
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if not (1 <= args.heap_gib <= 6) or not (30 <= args.timeout <= 900):
        parser.error("heap_gib must be 1..6 and timeout must be 30..900 seconds")
    return smoke_test(args)


if __name__ == "__main__":
    sys.exit(main())

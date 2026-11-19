#!/usr/bin/env python3
"""Bounded, non-mutating Forge dedicated-server smoke test of a verified candidate.

Stages ONLY in an OS temporary directory. The tracked pack, jars, worlds and
configs are never modified. No third-party jars are packaged as test artifacts.
The default profile validates minimal Forge+companion. The opt-in full profile
stages the tracked server mod set and current pack config/KubeJS sources in an
OS temporary directory. Neither profile launches a graphical client or tests
multiplayer. No staged world, third-party mod or binary is retained as evidence.

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
MIN_FULLPACK_JARS = 70
FULLPACK_REQUIRED_PREFIXES = (
    "Botania-", "MythicBotany-", "ars_nouveau-", "Mine_and_Slash-",
    "kubejs-forge-", "ftb-quests-forge-", "minecolonies-", "alfheim_leyworks-",
    "alfheim_golems-", "alfheim_companion-"
)


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
    assert alfheim_dimension_seen("ALFHEIM_DIMENSION_OK")
    assert not alfheim_dimension_seen("Unknown dimension mythicbotany:alfheim")
    assert 0 <= 120 <= 240
    assert requested_replies_seen("Companion profiles: X\nCompanion outfits: Y", False)
    assert not requested_replies_seen("Companion profiles: X\nCompanion outfits: Y", True)
    assert requested_replies_seen(
        "Companion profiles: X\nCompanion outfits: Y\nALFHEIM_DIMENSION_OK", True)
    with tempfile.TemporaryDirectory(prefix="alfheim-fullpack-preflight-") as missing:
        try:
            validate_full_pack(Path(missing))
        except ValueError:
            pass
        else:
            raise AssertionError("missing full pack directory was accepted")
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


def alfheim_dimension_seen(messages):
    return "ALFHEIM_DIMENSION_OK" in messages


def validate_full_pack(pack):
    """Fail closed on a partial mod set or missing pack configuration."""
    mod_dir = pack / "server" / "mods"
    if not mod_dir.is_dir():
        raise ValueError("full pack has no tracked server/mods directory")
    for required_dir in ("config", "defaultconfigs", "kubejs"):
        if not (pack / required_dir).is_dir():
            raise ValueError(f"full pack missing {required_dir}/")
    jars = sorted(mod_dir.glob("*.jar"))
    if len(jars) < MIN_FULLPACK_JARS:
        raise ValueError(f"Only {len(jars)} server JARs found; refusing partial-pack smoke")
    names = {jar.name for jar in jars}
    for prefix in FULLPACK_REQUIRED_PREFIXES:
        if not any(name.startswith(prefix) for name in names):
            raise ValueError(f"Required gameplay mod missing from full staging pack: {prefix}")
    return jars


def requested_replies_seen(messages, require_alfheim):
    return command_outputs_seen(messages) and (not require_alfheim or alfheim_dimension_seen(messages))


def stop_process(process):
    if process is None or process.poll() is not None:
        return
    try:
        process.terminate()
        process.wait(timeout=15)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=15)


def boot(stage, output, heap_gib, timeout, require_alfheim=False,
         hub_observe_seconds=0):
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
                    checks = ["alfheimcompanion profile list",
                              "alfheimcompanion outfit list"]
                    if require_alfheim:
                        checks.append("execute in mythicbotany:alfheim run say ALFHEIM_DIMENSION_OK")
                        checks.append(
                            "execute in mythicbotany:alfheim positioned 0 0 0 "
                            "positioned over motion_blocking_no_leaves "
                            "if predicate alfheim:hub/ground_height "
                            "run say ALFHEIM_GROUND_HEIGHT_OK")
                        checks.append(
                            "execute in mythicbotany:alfheim positioned 0 0 0 "
                            "positioned over motion_blocking_no_leaves "
                            "unless predicate alfheim:hub/ground_height "
                            "run say ALFHEIM_GROUND_HEIGHT_REJECTED")
                        # Marker has no collision and is deleted after the diagnostic.
                        checks.append(
                            'execute in mythicbotany:alfheim positioned 0 0 0 '
                            'positioned over motion_blocking_no_leaves '
                            'run summon minecraft:marker ~ ~ ~ {Tags:["alfheim_origin_probe"]}')
                        checks.append(
                            "execute in mythicbotany:alfheim run data get entity "
                            "@e[type=minecraft:marker,tag=alfheim_origin_probe,limit=1] Pos")
                        checks.append(
                            "execute in mythicbotany:alfheim run kill "
                            "@e[type=minecraft:marker,tag=alfheim_origin_probe]")
                        # These are read-only diagnostics, not a synthetic force-success.
                        checks.append("function alfheim:hub/status")
                        for stage_name in ("place_result", "base_result", "trunk_result",
                                           "crown_result", "court_result", "west_result",
                                           "east_result", "north_result", "attempts",
                                           "created", "final"):
                            checks.append(f"scoreboard players get #{stage_name} alfheim.hub")
                    checks.append("list")
                    command_started = time.monotonic()
                    for command_line in checks:
                        process.stdin.write(command_line + "\n")
                        process.stdin.flush()
                        time.sleep(0.25)
                    # Worldgen can stall the main tick thread even AFTER Forge logs Done.
                    # Don't start the shutdown timer before the queued commands run.
                    response_deadline = time.monotonic() + (210 if require_alfheim else 60)
                    while time.monotonic() < response_deadline and process.poll() is None:
                        if requested_replies_seen(read_log(log), require_alfheim):
                            break
                        time.sleep(2)
                    responses = requested_replies_seen(read_log(log), require_alfheim)
                    report["command_reply_latency_seconds"] = round(time.monotonic() - command_started, 1)
                    if not responses:
                        report["error"] = "Console commands were not answered within the bounded response window"
                    if require_alfheim and hub_observe_seconds > 0 and process.poll() is None:
                        # Give the bounded hub retry loop an actual opportunity to
                        # finish before diagnosing an incomplete spawn on a new world.
                        observation_started = time.monotonic()
                        while time.monotonic() - observation_started < hub_observe_seconds:
                            current = read_log(log)
                            if ("world hub anchored to the Greatbole" in current
                                    or "deterministic Greatbole and royal complex assembly succeeded"
                                    in current):
                                break
                            if process.poll() is not None:
                                break
                            time.sleep(2)
                        report["hub_observation_seconds"] = round(
                            time.monotonic() - observation_started, 1)
                        if process.poll() is None:
                            for command_line in (
                                "function alfheim:hub/status",
                                "scoreboard players get #place_result alfheim.hub",
                                "scoreboard players get #attempts alfheim.hub",
                                "scoreboard players get #final alfheim.hub",
                            ):
                                process.stdin.write(command_line + "\n")
                                process.stdin.flush()
                            time.sleep(3)
                    if process.poll() is None:
                        process.stdin.write("stop\n")
                        process.stdin.flush()
                        report["stop_command_sent"] = True
                        shutdown_started = time.monotonic()
                        try:
                            # The old timeout started 60s before the saturated server
                            # actually consumed the queued stop. Count from HERE instead.
                            process.wait(timeout=180 if require_alfheim else 75)
                        except subprocess.TimeoutExpired:
                            report["error"] = "Server did not finish shutdown after the bounded stop grace period"
                        report["shutdown_wait_seconds"] = round(time.monotonic() - shutdown_started, 1)
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
        report["alfheim_dimension_command_ok"] = alfheim_dimension_seen(final)
        report["hub_status_probed"] = "[Alfheim] --- world hub status ---" in final
        report["hub_created_diagnostic"] = "[Alfheim] hub: created" in final
        report["hub_initial_assembly_failed"] = "deterministic Greatbole template assembly failed" in final
        report["hub_anchored"] = "world hub anchored to the Greatbole" in final
        report["ground_height_predicate_ok"] = "ALFHEIM_GROUND_HEIGHT_OK" in final
        report["ground_height_predicate_rejected"] = "ALFHEIM_GROUND_HEIGHT_REJECTED" in final
        report["stop_acknowledged"] = ("Stopping the server" in final or "Stopping server" in final)
        report["all_dimensions_saved"] = "All dimensions are saved" in final
        replies_ok = requested_replies_seen(final, require_alfheim)
        if report["ready"] and report["exit_code"] == 0 and not replies_ok:
            report["error"] = ("Forge booted, but companion commands or Alfheim "
                               "dimension probe did not return their required replies")
        report["clean_exit"] = report["clean_exit"] and replies_ok
        report["last_log_lines"] = final.splitlines()[-35:]
        # Keep useful evidence bounded; upload no source jars or player/world files.
        if len(final.encode("utf-8")) > MAX_LOG_BYTES:
            log.write_text(final[-MAX_LOG_BYTES:], encoding="utf-8")
    return report


def smoke_test(args):
    output = Path(args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    report = {
        "profile": ("full-modpack-dedicated-server" if args.profile == "full"
                    else "minimal-forge-companion-dedicated-server"),
        "admission": ("full-pack startup and command smoke only; not graphical client, "
                      "save/reload or multiplayer" if args.profile == "full"
                      else "startup-smoke-only; not full pack, save, client or multiplayer"),
        "expected_candidate_sha256": args.expected_sha256,
        "source_commit": "f1a43100c45ba1efb52db673f624362774fa6f4f",
        "candidate_artifact_id": 14580075904,
        "candidate_build_run_id": 44626195977,
        "heap_gib": args.heap_gib,
        "timeout_seconds": args.timeout,
        "seed": args.seed,
        "hub_observe_requested_seconds": args.hub_observe_seconds,
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
            if args.profile == "full":
                pack = Path(args.pack_root).resolve()
                tracked = validate_full_pack(pack)
                report["tracked_mod_count"] = len(tracked)
                report["source_companion_sha256"] = sha256(pack / "server" / "mods" / JAR_NAME)
                report["third_party_mods_changed"] = False
                # Exclude old first-party JAR and generated Connector caches.
                for jar in tracked:
                    if jar.name != JAR_NAME:
                        shutil.copy2(jar, mods / jar.name)
                for folder in ("config", "defaultconfigs", "kubejs"):
                    shutil.copytree(pack / folder, stage / folder)
                report["pack_directories_staged"] = ["config", "defaultconfigs", "kubejs"]
            shutil.copy2(candidate, mods / JAR_NAME)
            report["staged_mod_count"] = len(list(mods.glob("*.jar")))
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
                f"level-seed={args.seed}\n"
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
            result = boot(stage, output, args.heap_gib, args.timeout,
                          require_alfheim=args.profile == "full",
                          hub_observe_seconds=args.hub_observe_seconds)
            report.update(result)
            report["success"] = result["ready"] and result["clean_exit"]
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        report["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        (output / "smoke-report.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if report["success"]:
        if args.profile == "full":
            print("COMPANION_FULLPACK_SMOKE_PASS: pinned JAR, full pack startup, Alfheim dimension, companion commands and clean stop")
        else:
            print("COMPANION_SERVER_SMOKE_PASS: exact SHA-256, minimal Forge ready, companion profile/outfit commands and clean stop")
        return 0
    print("COMPANION_SERVER_SMOKE_FAIL: " + str(report.get("error", report.get("last_log_lines", [])[-5:])))
    return 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--profile", choices=("minimal", "full"), default="minimal")
    parser.add_argument("--seed", default="alfheim")
    parser.add_argument("--hub-observe-seconds", type=int, default=0)
    parser.add_argument("--pack-root", default="fullpack-source")
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
    if not (0 <= args.hub_observe_seconds <= 240):
        parser.error("hub-observe-seconds must be 0..240")
    return smoke_test(args)


if __name__ == "__main__":
    sys.exit(main())

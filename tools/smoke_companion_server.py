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
# The protected Royal Court is an inclusive 10x10 chunk rectangle.
FTB_EXPECTED_SPAWN_CLAIMS = 100
FTB_CLAIM_READY = re.compile(
    r"\[Alfheim Reclaimed\] spawn hub FTB claim READY\b[^\n]*"
    r"FTB ownership verified (\d+)/(\d+) chunks for alfheim_hub\."
)
FTB_ALREADY_CLAIMED = re.compile(
    r"\[Alfheim Reclaimed\] spawn claim -?\d+,-?\d+ returned already_claimed\b"
)
TICK_LAG_REPORT = re.compile(
    r"Can't keep up! Is the server overloaded\? Running (\d+)ms or (\d+) ticks behind"
)
HUB_STAGE_SCORES = (
    "base_result", "trunk_result", "crown_result", "court_result",
    "west_result", "east_result", "north_result",
)
# A saved entity can become queryable several ticks after the dimension loads.
# Preserve strict acceptance, but do not mistake one immediate lookup for loss.
RESTART_MARKER_GRACE_SECONDS = 60
ANCHOR_PROBE = (
    "execute in mythicbotany:alfheim if entity "
    "@e[type=minecraft:marker,tag=alfheim_hub_baked,"
    "tag=!alfheim_hub_buried,limit=1] "
    "run say ALFHEIM_BAKED_ANCHOR_PRESENT"
)
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
    fixture = "\n".join(
        f"#{key} has 1 [alfheim.hub]"
        for key in ("place_result", "created", "final", *HUB_STAGE_SCORES))
    assert latest_hub_score(fixture, "final") == 1
    assert latest_hub_score(fixture + "\n#final has 2 [alfheim.hub]", "final") == 2
    assert latest_hub_score(fixture, "attempts") is None
    hub_fixture = {"hub_scores": {key: 1 for key in
                   ("place_result", "created", "final", *HUB_STAGE_SCORES)},
                   "hub_baked_marker_present": True,
                   "hub_assembled_this_boot": False}
    assert hub_snapshot_accepted(hub_fixture, restarted=True)
    assert 0 < RESTART_MARKER_GRACE_SECONDS <= 120
    assert "tag=alfheim_hub_baked" in ANCHOR_PROBE
    assert "ALFHEIM_BAKED_ANCHOR_PRESENT" in ANCHOR_PROBE
    assert not hub_snapshot_accepted({**hub_fixture, "hub_assembled_this_boot": True},
                                     restarted=True)
    assert not hub_snapshot_accepted({**hub_fixture, "hub_baked_marker_present": False})
    claim_ready_fixture = (
        "[23:50:34] [Server thread/INFO] [KubeJS Server/]: 04_spawn_hub.js#210: "
        "[Alfheim Reclaimed] spawn hub FTB claim READY (other protections require runtime checks): "
        "no-hostile-spawns, no-explosions; FTB ownership verified 100/100 chunks for alfheim_hub.")
    previous_warning = (
        "[23:50:34] [Server thread/WARN] [KubeJS Server/]: 04_spawn_hub.js#196: "
        "[Alfheim Reclaimed] spawn claim -5,-8 returned already_claimed")
    pristine = full_pack_observations(claim_ready_fixture)
    assert full_pack_claims_accepted(pristine, require_clean_reload=True)
    noisy = full_pack_observations(claim_ready_fixture + "\n" + previous_warning)
    assert noisy["ftb_redundant_claim_warnings"] == 1
    assert not full_pack_claims_accepted(noisy, require_clean_reload=True)
    assert full_pack_claims_accepted(noisy, require_clean_reload=False)
    assert not full_pack_claims_accepted(
        full_pack_observations(claim_ready_fixture.replace("100/100", "99/100")))
    assert not full_pack_claims_accepted(
        full_pack_observations(claim_ready_fixture.replace("100/100", "100/101")))
    assert not full_pack_claims_accepted(full_pack_observations(""))
    lag_example = full_pack_observations(
        claim_ready_fixture + "\n"
        "[23:48:04] [Server thread/WARN] [minecraft/MinecraftServer]: "
        "Can't keep up! Is the server overloaded? Running 54058ms or 1081 ticks behind")
    assert lag_example["server_tick_lag_max_ms"] == 54058
    assert lag_example["server_tick_lag_events"] == 1
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


def full_pack_observations(messages):
    """Return real claim ownership and startup lag readings from one boot only."""
    ready = FTB_CLAIM_READY.findall(messages)
    owner_count, expected_count = (tuple(map(int, ready[-1])) if ready
                                   else (None, None))
    lag = [int(milliseconds) for milliseconds, _ in TICK_LAG_REPORT.findall(messages)]
    return {
        "ftb_claims_owned": owner_count,
        "ftb_claims_expected": expected_count,
        "ftb_redundant_claim_warnings": len(FTB_ALREADY_CLAIMED.findall(messages)),
        "ftb_foreign_claim_conflicts": messages.count("[Alfheim Reclaimed] hub claim conflict at "),
        "server_tick_lag_max_ms": max(lag, default=0),
        "server_tick_lag_events": len(lag)
    }


def full_pack_claims_accepted(result, require_clean_reload=False):
    return (result.get("ftb_claims_owned") == FTB_EXPECTED_SPAWN_CLAIMS
            and result.get("ftb_claims_expected") == FTB_EXPECTED_SPAWN_CLAIMS
            and result.get("ftb_foreign_claim_conflicts") == 0
            and (not require_clean_reload or result.get("ftb_redundant_claim_warnings") == 0))


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


def latest_hub_score(messages, name):
    # The live dedicated server prints: #final has 1 [alfheim.hub]
    values = re.findall(
        rf"(?m)^.*#{re.escape(name)} has (-?\d+) \[alfheim\.hub\]\s*$", messages)
    return int(values[-1]) if values else None


def hub_snapshot_accepted(report, restarted=False):
    if not all(report.get("hub_scores", {}).get(name) == 1
               for name in ("place_result", "created", "final", *HUB_STAGE_SCORES)):
        return False
    if not report.get("hub_baked_marker_present"):
        return False
    if restarted and report.get("hub_assembled_this_boot"):
        # A previously completed structure must not be generated again on load.
        return False
    return True


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
         hub_observe_seconds=0, log_name="server-console.log",
         marker_grace_seconds=0):
    log = output / log_name
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
                        checks.append(ANCHOR_PROBE)
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
                    if (require_alfheim and marker_grace_seconds > 0
                            and process.poll() is None):
                        # The origin may be loaded before its saved marker is
                        # admitted to the entity selector after world restart.
                        # Query the REAL saved marker repeatedly; never summon,
                        # fabricate or modify it to force a test success.
                        started_grace = time.monotonic()
                        attempts = 0
                        while (time.monotonic() - started_grace < marker_grace_seconds
                               and process.poll() is None):
                            if "ALFHEIM_BAKED_ANCHOR_PRESENT" in read_log(log):
                                break
                            process.stdin.write(ANCHOR_PROBE + "\n")
                            process.stdin.flush()
                            attempts += 1
                            time.sleep(3)
                        report["anchor_probe_attempts"] = attempts
                        report["anchor_probe_wait_seconds"] = round(
                            time.monotonic() - started_grace, 1)
                        report["anchor_recovered_during_grace"] = (
                            "ALFHEIM_BAKED_ANCHOR_PRESENT" in read_log(log))
                        if not report["anchor_recovered_during_grace"]:
                            report["error"] = (
                                "Saved Greatbole baked marker was not selectable "
                                "within bounded restart grace period")
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
        report["hub_baked_marker_present"] = "ALFHEIM_BAKED_ANCHOR_PRESENT" in final
        report["hub_assembled_this_boot"] = (
            "deterministic Greatbole and royal complex assembly succeeded" in final)
        report["hub_scores"] = {name: latest_hub_score(final, name)
                                for name in ("place_result", "created", "final", "attempts",
                                             *HUB_STAGE_SCORES)}
        report["hub_initial_assembly_failed"] = "deterministic Greatbole template assembly failed" in final
        report["hub_anchored"] = "world hub anchored to the Greatbole" in final
        report["ground_height_predicate_ok"] = "ALFHEIM_GROUND_HEIGHT_OK" in final
        report["ground_height_predicate_rejected"] = "ALFHEIM_GROUND_HEIGHT_REJECTED" in final
        report["stop_acknowledged"] = ("Stopping the server" in final or "Stopping server" in final)
        report["all_dimensions_saved"] = "All dimensions are saved" in final
        report.update(full_pack_observations(final))
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
        "verify_restart": args.verify_restart,
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
            report["first_ftb_claims_accepted"] = (
                full_pack_claims_accepted(result) if args.profile == "full" else None)
            report["success"] = (result["ready"] and result["clean_exit"]
                                 and (args.profile != "full"
                                      or report["first_ftb_claims_accepted"]))
            if args.profile == "full" and not report["first_ftb_claims_accepted"]:
                report["error"] = ("First boot did not verify all 100/100 "
                                   "administrative spawn claims")
            if args.verify_restart:
                report["first_hub_accepted"] = hub_snapshot_accepted(result)
                if not report["success"] or not report["first_hub_accepted"]:
                    raise ValueError("First boot did not prove completed Greatbole and clean save")
                world = stage / "ci-alfheim-companion-smoke"
                level_file = world / "level.dat"
                if not level_file.is_file():
                    raise ValueError("First server did not persist level.dat before restart")
                report["world_level_dat_sha256_before_restart"] = sha256(level_file)
                if sha256(mods / JAR_NAME) != actual:
                    raise ValueError("Staged companion JAR changed during first boot")
                # Reuse EXACTLY the same temporary world, mods, settings and Java 17
                # runtime. A fresh log prevents borrowing the first boot's success.
                restart = boot(stage, output, args.heap_gib, args.timeout,
                               require_alfheim=True, hub_observe_seconds=0,
                               log_name="server-console-restart.log",
                               marker_grace_seconds=RESTART_MARKER_GRACE_SECONDS)
                report["restart"] = restart
                report["world_level_dat_sha256_after_restart"] = (
                    sha256(level_file) if level_file.is_file() else None)
                report["restart_hub_accepted"] = hub_snapshot_accepted(
                    restart, restarted=True)
                report["restart_ftb_claims_accepted"] = full_pack_claims_accepted(
                    restart, require_clean_reload=True)
                same_attempts = (
                    result["hub_scores"].get("attempts") ==
                    restart["hub_scores"].get("attempts") and
                    result["hub_scores"].get("attempts") is not None)
                report["hub_attempts_unchanged_after_restart"] = same_attempts
                report["success"] = (restart["ready"] and restart["clean_exit"]
                                     and report["restart_hub_accepted"]
                                     and report["restart_ftb_claims_accepted"]
                                     and same_attempts
                                     and bool(report["world_level_dat_sha256_after_restart"])
                                     and sha256(mods / JAR_NAME) == actual)
                if not report["success"]:
                    report["error"] = (
                        "Saved-world restart failed: Greatbole, companion, FTB 100/100 "
                        "claim ownership, redundant already_claimed warnings, or clean stop")
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        report["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        (output / "smoke-report.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if report["success"]:
        if args.verify_restart:
            print("COMPANION_FULLPACK_RESTART_PASS: pinned JAR, saved-world reload, seven Greatbole pieces, 100/100 claims, zero redundant claim warnings and clean stop")
        elif args.profile == "full":
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
    parser.add_argument("--verify-restart", action="store_true",
                        help="boot the same saved full-pack world twice and reject repeated hub creation")
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
    if args.verify_restart and args.profile != "full":
        parser.error("--verify-restart requires --profile full")
    return smoke_test(args)


if __name__ == "__main__":
    sys.exit(main())

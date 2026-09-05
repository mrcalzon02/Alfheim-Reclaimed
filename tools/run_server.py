"""Headless dedicated-server harness: generate and validate a world from the command line.

Every runtime claim in this project has been deferred because booting meant driving the
CurseForge GUI. A Forge dedicated server needs no GUI, so levels 8, 9 and 10 of the validation
ladder become scriptable: launch, generate, run a command sequence, capture the console, stop.

    python tools/run_server.py --check      # prerequisites only, mutates nothing (default)
    python tools/run_server.py --install    # unpack the Forge server into server/
    python tools/run_server.py --run        # build runtime, launch, run the script, stop

WHAT THIS DOES NOT DO WITHOUT BEING TOLD
----------------------------------------
`--install` downloads: the Forge installer fetches the vanilla server jar from Mojang and
Forge's own artifacts from maven. `--run` requires `server/eula.txt` to contain `eula=true`,
which is Mojang's licence agreement and is the user's to accept, not this script's. Neither is
done implicitly; `--check` reports both as missing and stops.

LAYOUT
------
    server/                     Forge server install + runtime. NEVER PACKAGED -- see below.
      libraries/                written by the installer
      run.bat / win_args.txt    the loader's own bootstrap
      eula.txt                  yours to write
      mods/ config/ kubejs/     mirrored from the instance at run time
      world/                    generated
      logs/, console.log        runtime evidence

`server/` is development tooling under INSTRUCTIONS.md §5's `tools/` rule: never packaged, never
placed in a distributable. A CurseForge export must exclude it -- it contains a Mojang server jar
that cannot be redistributed.
"""
import argparse
import glob
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

MC = '1.20.1'
FORGE = '47.4.10'
INSTALL = os.path.join('C:' + os.sep, 'Users', 'Admin', 'curseforge', 'minecraft', 'Install')
JAVA17 = os.path.join(INSTALL, 'java', 'java-runtime-gamma', 'bin', 'java.exe')
SERVER = 'server'
INSTALLER = os.path.join(SERVER, f'forge-{MC}-{FORGE}-installer.jar')
INSTALLER_URL = (f'https://maven.minecraftforge.net/net/minecraftforge/forge/'
                 f'{MC}-{FORGE}/forge-{MC}-{FORGE}-installer.jar')

# Mirrored into the server runtime. Everything the pack's behaviour actually lives in.
MIRROR = ['mods', 'config', 'defaultconfigs', 'kubejs', 'datapacks']

# Mods omitted from a dedicated server run.
#
# This is a SERVER-RUN policy, not a pack change: these jars still ship to clients. Omitting one
# here only means a headless validation run does not load it.
#
# No Forge jar declares `side="CLIENT"` at mod level, so the first boot loaded all 82 and failed
# in dependency resolution rather than anywhere obvious. The cause was Sinytra Connector: three
# FABRIC mods are present and loaded through it, and Connector resolves their dependencies
# against the running environment.
#
#   continuity   fabric.mod.json environment="client"   <- cannot run on a dedicated server
#   buildguide   environment="*", client entrypoint only -- loads, does nothing, harmless
#   pehkui       environment="*", main entrypoint        -- genuinely both sides
#
# Only the first is a real conflict. It is a connected-textures mod: there is nothing for it to
# do without a renderer.
# Boot 2 then named a second, different cause. Entity Texture Features puts a client-dependent
# handler in a COMMON mixin -- `ResourceLocation.handler$...$etf$illegalPathOverride` reaches for
# `net/minecraft/client/gui/screens/Screen`, which the dist cleaner refuses on a dedicated
# server, and the whole bootstrap dies in SharedConstants.<clinit>.
#
# That is a mod defect, not a pack defect: a properly guarded mod puts client code in the
# `client` mixin block, where Mixin applies it only on a client. 30 other jars here have client
# mixin blocks and are fine for exactly that reason, which is why the omit list is short rather
# than "everything that renders".
SERVER_MOD_OMIT = [
    'continuity-3.0.0+1.20.1.forge.jar',
    'entity_texture_features_1.20.1-forge-7.1.jar',
    'entity_model_features-3.2.4-1.20.1-forge.jar',
    # Boot 3 named two more of the same kind, both failing the dist cleaner outright:
    #   BetterGrassify  -> net/minecraft/client/gui/screens/Screen
    #   ForgeSkyboxes   -> net/minecraft/client/Options
    # Both are pure client-render mods with nothing to contribute to a headless world.
    'BetterGrassify-1.4.4+forge.1.20.1.jar',
    'forgeskyboxes-0.0.2-1.20.2-new.jar',
]


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def check(verbose=True):
    """Report what is present and what is missing. Mutates nothing."""
    ok = True

    def line(good, label, detail=''):
        nonlocal ok
        if not good:
            ok = False
        print(f'  {"OK  " if good else "MISS"}  {label:34} {detail}')

    print('prerequisites')
    line(os.path.exists(JAVA17), 'Java 17', JAVA17 if os.path.exists(JAVA17) else 'not found')
    line(os.path.isdir('mods'), 'instance mods/',
         f'{len(glob.glob(os.path.join("mods", "*.jar")))} jars')
    line(os.path.isdir('kubejs'), 'instance kubejs/')

    print('\nserver install')
    argfile = os.path.join(SERVER, 'libraries', 'net', 'minecraftforge', 'forge',
                           f'{MC}-{FORGE}', 'win_args.txt')
    line(os.path.exists(INSTALLER), 'Forge installer jar',
         INSTALLER if os.path.exists(INSTALLER) else f'download from {INSTALLER_URL}')
    line(os.path.exists(argfile), 'Forge server argfile',
         argfile if os.path.exists(argfile) else 'run --install')

    eula = os.path.join(SERVER, 'eula.txt')
    accepted = (os.path.exists(eula)
                and 'eula=true' in open(eula, encoding='utf-8').read().lower())
    line(accepted, 'eula.txt accepted',
         'accepted' if accepted else 'REQUIRED, and it is yours to accept, not mine')

    print()
    print('ready to run' if ok else 'not ready -- see MISS above')
    return 0 if ok else 1


def install():
    if not os.path.exists(INSTALLER):
        print(f'!! installer not present at {INSTALLER}')
        print(f'   download it from {INSTALLER_URL}')
        return 2
    os.makedirs(SERVER, exist_ok=True)
    print(f'installer sha256 {sha256(INSTALLER)}')
    r = subprocess.run([JAVA17, '-jar', os.path.abspath(INSTALLER), '--installServer', '.'],
                       cwd=SERVER, capture_output=True, text=True)
    print(r.stdout[-3000:])
    if r.returncode != 0:
        print(r.stderr[-3000:])
    return r.returncode


def running_servers():
    """PIDs of server processes already launched from this harness.

    Runs 3 through 5 taught this the hard way: when the wrapper is killed, the java child
    survives, keeps `session.lock` on the world, and the next run dies with

        java.io.IOException: The process cannot access the file because another process
        has locked a portion of the file   (net.minecraft.util.DirectoryLock)

    which reads like a filesystem problem and is actually a stale server. Detect it instead.
    """
    try:
        r = subprocess.run(
            ['powershell', '-NoProfile', '-Command',
             "Get-CimInstance Win32_Process -Filter \"Name='java.exe'\" | "
             "Where-Object { $_.CommandLine -like '*forge*win_args*' } | "
             "Select-Object -ExpandProperty ProcessId"],
            capture_output=True, text=True, timeout=60)
        return [int(x) for x in r.stdout.split() if x.strip().isdigit()]
    except Exception:
        return []


def mirror_instance():
    """Copy the pack into the server runtime.

    Copied rather than linked on purpose: the server rewrites config/ on every boot (FTB Quests
    alphabetises its SNBT, mods normalise their TOML), and letting it write through to the
    instance would mean a validation run silently editing the thing being validated.
    """
    total = 0
    for d in MIRROR:
        if not os.path.isdir(d):
            continue
        dst = os.path.join(SERVER, d)
        if os.path.isdir(dst):
            shutil.rmtree(dst)
        shutil.copytree(d, dst)
        n = sum(len(f) for _, _, f in os.walk(dst))
        total += n
        print(f'  mirrored {d:16} {n:>5} files')
    # A misspelled omit entry silently omits nothing, and the next boot fails for a reason you
    # already thought you had fixed. Say so loudly instead.
    for name in SERVER_MOD_OMIT:
        p = os.path.join(SERVER, 'mods', name)
        if os.path.exists(p):
            os.remove(p)
            print(f'  omitted  {name}')
        else:
            print(f'  !! OMIT ENTRY MATCHED NOTHING: {name} -- check the filename')
    return total


def write_properties(seed, level_name):
    props = {
        'level-name': level_name,
        'level-seed': seed,
        'online-mode': 'false',
        'gamemode': 'creative',
        'max-tick-time': '-1',          # a slow chunk is not a crash; do not watchdog-kill it
        'view-distance': '8',
        'simulation-distance': '6',
        'spawn-protection': '0',
        'sync-chunk-writes': 'false',
        'motd': 'Alfheim Reclaimed - headless validation',
    }
    with open(os.path.join(SERVER, 'server.properties'), 'w', encoding='utf-8') as f:
        for k, v in sorted(props.items()):
            f.write(f'{k}={v}\n')
    return props


def run(seed, level_name, heap, commands, timeout):
    argfile = os.path.join('libraries', 'net', 'minecraftforge', 'forge',
                           f'{MC}-{FORGE}', 'win_args.txt')
    if not os.path.exists(os.path.join(SERVER, argfile)):
        print('!! no server argfile; run --install first')
        return 2
    eula = os.path.join(SERVER, 'eula.txt')
    if not (os.path.exists(eula)
            and 'eula=true' in open(eula, encoding='utf-8').read().lower()):
        print('!! server/eula.txt does not say eula=true.')
        print('   That is Mojang\'s licence agreement and it is yours to accept, not mine.')
        return 2

    stale = running_servers()
    if stale:
        print(f'!! {len(stale)} server process(es) already running: {stale}')
        print('   They hold the world lock. Stop them before launching another:')
        for pid in stale:
            print(f'     taskkill /PID {pid} /F')
        return 2

    # A lock left by a killed server blocks startup even though nothing owns it any more.
    lock = os.path.join(SERVER, level_name, 'session.lock')
    if os.path.exists(lock):
        os.remove(lock)
        print(f'cleared stale {lock}')

    print('mirroring instance into server runtime')
    mirror_instance()
    props = write_properties(seed, level_name)

    cmd = [JAVA17, f'-Xmx{heap}G', f'-Xms{min(heap, 4)}G', f'@{argfile}', 'nogui']
    print(f'launching: {" ".join(cmd)}')
    stamp = time.strftime('%Y%m%d-%H%M%S')
    console = os.path.join(SERVER, f'console-{stamp}.log')
    started = time.time()
    harness_exit = 0
    with open(console, 'w', encoding='utf-8', errors='replace') as log:
        p = subprocess.Popen(cmd, cwd=SERVER, stdin=subprocess.PIPE, stdout=log,
                             stderr=subprocess.STDOUT, text=True, bufsize=1)
        # Commands are fed on stdin after a delay rather than on a "Done" match, because a
        # crash during worldgen never prints Done and we would wait forever for it.
        try:
            for delay, line in commands:
                time.sleep(delay)
                if p.poll() is not None:
                    print(f'server exited early with {p.returncode} before: {line}')
                    harness_exit = 3
                    break
                p.stdin.write(line + '\n')
                p.stdin.flush()
                print(f'  -> {line}')
            p.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            harness_exit = 124
            print(f'!! still running after {timeout}s; terminating')
            p.terminate()
            try:
                p.wait(timeout=60)
            except subprocess.TimeoutExpired:
                p.kill()
                p.wait()
        except Exception as e:
            harness_exit = 2
            print(f'!! {e}')
            p.kill()
            p.wait()

    if harness_exit == 0 and p.returncode not in (None, 0):
        harness_exit = 1

    elapsed = round(time.time() - started, 1)
    manifest = {
        'minecraft': MC, 'forge': FORGE, 'seed': seed, 'level_name': level_name,
        'heap_gib': heap, 'elapsed_s': elapsed, 'exit_code': p.returncode,
        'harness_exit_code': harness_exit,
        'properties': props, 'omitted_mods': SERVER_MOD_OMIT,
        'mods_jars': len(glob.glob(os.path.join(SERVER, 'mods', '*.jar'))),
        'commands': [c for _, c in commands],
        'console': os.path.basename(console),
    }
    with open(os.path.join(SERVER, f'manifest-{stamp}.json'), 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    print(f'\nexit {p.returncode} after {elapsed}s; harness exit {harness_exit}; console -> {console}')
    return harness_exit


DEFAULT_COMMANDS = [
    (90, 'say alfheim validation: startup reached'),
    # Ground truth for every registry. Lang-derived ids are NOT proof of registration --
    # Mine and Slash ships `item.mmorpg.map` in its lang file and does not register
    # `mmorpg:map`, which silently rejected 11 bridge recipes. Dump the real registry and
    # check against that instead of against translations.
    # `kubejs export` is deliberately NOT here. It triggers a datapack reload that fails on
    # this build with
    #     NoSuchMethodError: boolean com.google.gson.JsonObject.isEmpty()
    # -- gson 2.10 on the classpath, and that method arrives in 2.10.1. The export itself
    # still writes, but the failed reload leaves "Reload failed; keeping old data" in the log
    # and muddies a validation run. Use --export when you actually want a fresh registry dump.
    # World-hub verification. #minecraft:load should have created the hub before this runs,
    # with no player connected -- that is the whole point of the design.
    (5, 'function alfheim:hub/status'),
    (5, 'execute in mythicbotany:alfheim run forceload query'),
    # Biome reachability probe. `locate biome` either reports a distance or says it could not
    # find one -- which is the only honest way to know whether a band in the layer actually
    # gets selected. Nine of ours were unreachable by construction until 2026-09-04 because
    # MythicBotany ships temperature and humidity as constant 0.0.
    (2, 'execute in mythicbotany:alfheim positioned 0 100 0 run locate biome alfheim:ashen_grove'),
    (2, 'execute in mythicbotany:alfheim positioned 0 100 0 run locate biome alfheim:silverbark_wood'),
    (2, 'execute in mythicbotany:alfheim positioned 0 100 0 run locate biome alfheim:bloomfall_vale'),
    (2, 'execute in mythicbotany:alfheim positioned 0 100 0 run locate biome alfheim:mana_fen'),
    (2, 'execute in mythicbotany:alfheim positioned 0 100 0 run locate biome alfheim:sundered_highlands'),
    (2, 'execute in mythicbotany:alfheim positioned 0 100 0 run locate biome alfheim:hollow_marches'),
    (2, 'execute in mythicbotany:alfheim positioned 0 100 0 run locate biome alfheim:starved_reach'),
    (2, 'execute in mythicbotany:alfheim positioned 0 100 0 run locate biome alfheim:scorchfell'),
    (2, 'execute in mythicbotany:alfheim positioned 0 100 0 run locate biome alfheim:infested_warren'),
    (2, 'execute in mythicbotany:alfheim positioned 0 100 0 run locate biome alfheim:decayed_mire'),
    (2, 'execute in mythicbotany:alfheim positioned 0 100 0 run locate biome alfheim:void_verge'),
    # --- MIDGARD: does Continuity Works actually reach the Overworld? -----------------------
    #
    # Reported by the user 2026-09-04: "overall still had vanilla biomes not continuity works."
    #
    # Everything upstream of the world looks right -- TerraBlender logs
    #   Registered region continuityworks_biomes:overworld_templates to index 1 for type OVERWORLD
    # config/continuityworks-biomes-common.toml has every family enabled and regionWeight at its
    # maximum of 20, and the jar ships 146 biome definitions. None of that is evidence that a
    # single chunk of it generates. `locate biome` is: it either reports a distance or says it
    # could not find one, which is the same instrument that proved nine of our eleven Alfheim
    # biomes were unreachable on 2026-09-04.
    #
    # Probes are deliberately mixed -- two CW templates (the 8-entry tag the region is named
    # for), two CW anthology biomes (the 128-entry tag behind isAnthologyEnabled), one Regions
    # Unexplored biome as a second TerraBlender injector, and one vanilla biome as the control.
    # If the vanilla control is the only hit, the Overworld is not being injected at all; if the
    # templates hit and the anthology does not, the anthology switch is the suspect.
    (5, 'execute in minecraft:overworld positioned 0 100 0 run locate biome '
        'continuityworks_biomes:temperate_grove'),
    (2, 'execute in minecraft:overworld positioned 0 100 0 run locate biome '
        'continuityworks_biomes:misty_highlands'),
    (2, 'execute in minecraft:overworld positioned 0 100 0 run locate biome '
        'continuityworks_biomes:amber_forest'),
    (2, 'execute in minecraft:overworld positioned 0 100 0 run locate biome '
        'continuityworks_biomes:neon_city_grid'),
    (2, 'execute in minecraft:overworld positioned 0 100 0 run locate biome '
        'regions_unexplored:alpha_grove'),
    (2, 'execute in minecraft:overworld positioned 0 100 0 run locate biome '
        'minecraft:plains'),

    (5, 'forceload add -16 -16 16 16'),
    (30, 'execute in mythicbotany:alfheim run forceload add -16 -16 16 16'),

    # --- the spawn hub, verified rather than assumed -----------------------------------------
    #
    # Three separate failures hid behind "the hub exists", and each needs its own probe:
    #
    #   1. DID IT GENERATE AT ALL?  The structure's `biomes` field is a validity test, so a
    #      narrow #alfheim:has_greatbole meant no tree anywhere. `locate structure` is the only
    #      honest answer.
    #   2. IS IT AT THE ORIGIN?  concentric_rings snaps ring 0 to a preferred_biomes match up to
    #      112 blocks away, which is what desynchronised the claim and the spawn anchor from the
    #      tree. locate prints the coordinates, so the displacement is measurable.
    #   3. DID THE CANOPY SURVIVE?  Every piece was individually legal and the crown was culled
    #      anyway for overrunning max_distance_from_center. The probe marker baked into
    #      greatbole/crown answers this and nothing else does.
    (30, 'execute in mythicbotany:alfheim positioned 0 100 0 run locate structure '
         'alfheim:greatbole'),

    # WHICH BIOME IS AT THE ORIGIN? Answered from the `locate biome` block above, not by a
    # probe of its own: `execute if biome` does NOT exist in 1.20.1 -- Brigadier parses `if b`
    # as `if blocks` and fails with "Expected integer". It arrives in a later version.
    #
    # The distances do the job instead. On 2026-09-04 the nearest of our eleven was mana_fen at
    # 160 blocks, so the origin belongs to one of MythicBotany's five; of those only
    # alfheim_lakes is outside #alfheim:has_greatbole. The Greatbole duly appeared 135 blocks
    # out at [96, ~, -96] -- the designed fallback relocating off water, not a placement bug.
    # If a future run shows one of our biomes at distance ~0 AND the tree still displaced, that
    # deduction no longer holds and the cause is something else.
    (5, 'execute in mythicbotany:alfheim run data get entity '
        '@e[type=minecraft:marker,tag=alfheim_crown_probe,limit=1] Pos'),
    (5, 'execute in mythicbotany:alfheim run data get entity '
        '@e[type=minecraft:marker,tag=alfheim_hub_baked,limit=1] Pos'),
    # The court rides in the amphitheatre piece, so finding a seated elf proves that
    # branch placed too -- the court jigsaw is horizontal and fails independently of the
    # vertical trunk chain.
    (5, 'execute in mythicbotany:alfheim run data get entity '
        '@e[type=richs_races_wood_elves:wood_elf,limit=1] CustomName'),

    # Late status: hub/resolve retries every 5s until the chunks finish generating, so an
    # early status call can legitimately report NOT CREATED. This one runs after the
    # force-loads above have had time to land.
    (10, 'function alfheim:hub/status'),
    (5, 'execute in mythicbotany:alfheim run forceload query'),

    # FTB Chunks claim acceptance needs ownership read-back, not the return value from
    # `claim_as`. FTB Chunks `info` reports the owning team for the addressed chunk to an
    # operator/console source. Probe the centre and all four corners of the 192-block square
    # that 04_spawn_hub.js reconciles so the next headless run records whether the whole
    # relocation envelope belongs to the `alfheim_hub` server team.
    (2, 'ftbchunks info 0 0 mythicbotany:alfheim'),
    (2, 'ftbchunks info 192 192 mythicbotany:alfheim'),
    (2, 'ftbchunks info -192 192 mythicbotany:alfheim'),
    (2, 'ftbchunks info 192 -192 mythicbotany:alfheim'),
    (2, 'ftbchunks info -192 -192 mythicbotany:alfheim'),

    (60, 'save-all flush'),
    (20, 'stop'),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--install', action='store_true')
    ap.add_argument('--run', action='store_true')
    ap.add_argument('--seed', default='alfheim')
    ap.add_argument('--level-name', default='validation')
    ap.add_argument('--heap', type=int, default=8)
    ap.add_argument('--timeout', type=int, default=900)
    ap.add_argument('--export', action='store_true',
                    help='also dump the item registry (triggers a reload that fails on gson 2.10)')
    a = ap.parse_args()

    if a.install:
        return install()
    if a.run:
        cmds = list(DEFAULT_COMMANDS)
        if a.export:
            cmds.insert(1, (5, 'kubejs export'))
        return run(a.seed, a.level_name, a.heap, cmds, a.timeout)
    return check()


if __name__ == '__main__':
    sys.exit(main())

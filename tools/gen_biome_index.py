"""Generate the authoritative index of Alfheim's biomes and world parameters.

    python tools/gen_biome_index.py            # write alfheim_reclaimed_design/BIOME_INDEX.md
    python tools/gen_biome_index.py --check    # fail if the checked-in file is stale

WHY THIS IS GENERATED RATHER THAN WRITTEN. Every fact in the document already exists somewhere
in the pack: the emitted biome layer, the biome JSONs, MythicBotany's own five biomes inside its
jar, the density functions, the surface rule set, the structure biome tags and the deep geology
table in gen_deep_terrain. A hand-written index would be a second copy of all of it, and the
2026-09-07 field review is a long record of what happens when a second copy drifts from the
first. This reads the shipping data and reports it, so the index cannot claim a biome condition
the world does not actually use.

The one number the generator computes rather than reads is the climate region size. It is
base_period / xz_scale, where base_period is 2^-firstOctave of the vanilla noise the axis
borrows -- read from the client jar, not assumed.
"""
import argparse
import collections
import glob
import json
import os
import re
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NS = 'alfheim'
OUT = os.path.join(ROOT, 'alfheim_reclaimed_design', 'BIOME_INDEX.md')

# GenerationStep.Decoration, in order. A biome's `features` list is indexed by this.
STEPS = ['raw_generation', 'lakes', 'local_modifications', 'underground_structures',
         'surface_structures', 'strongholds', 'underground_ores', 'underground_decoration',
         'fluid_springs', 'vegetal_decoration', 'top_layer_modification']

AXES = ['continentalness', 'erosion', 'weirdness', 'temperature', 'humidity']
AXIS_SHORT = {'continentalness': 'cont', 'erosion': 'eros', 'weirdness': 'weird',
              'temperature': 'temp', 'humidity': 'humid'}

# The vanilla noises each Alfheim climate axis borrows, and the density function that wraps it.
CLIMATE_AXES = [('temperature', 'alfheim_temperature'),
                ('humidity', 'alfheim_humidity'),
                ('weirdness', 'alfheim_weirdness'),
                ('continentalness', 'alfheim_continentalness')]

# "Nothing grows" is absolute in the Void -- no mushrooms, brambles, trees, grass or other
# living ground cover. These six are therefore exempt from the vegetation coverage check in §5
# rather than counted as gaps.
VOID_BIOMES = {'void_verge', 'starless_reach', 'shatterfields', 'prism_drift', 'rootfall',
               'sepulchral_reach'}

CLIENT_JARS = [
    'C:/Users/Admin/curseforge/minecraft/Install/versions/1.20.1/1.20.1.jar',
    os.path.join(ROOT, '..', '..', 'Install', 'versions', '1.20.1', '1.20.1.jar'),
]


def read_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def mb_jar():
    return zipfile.ZipFile(glob.glob(os.path.join(ROOT, 'mods', 'MythicBotany*.jar'))[0])


def client_jar():
    for p in CLIENT_JARS:
        if os.path.exists(p):
            return zipfile.ZipFile(p)
    return None


# --- collection -------------------------------------------------------------------------------

def load_biomes():
    """Ours from the datapack, MythicBotany's five from its jar. Both ship; both count."""
    out = {}
    for p in sorted(glob.glob(os.path.join(ROOT, 'kubejs/data/alfheim/worldgen/biome/*.json'))):
        out[f'{NS}:' + os.path.basename(p)[:-5]] = read_json(p)
    z = mb_jar()
    for n in z.namelist():
        if n.startswith('data/mythicbotany/worldgen/biome/') and n.endswith('.json'):
            out['mythicbotany:' + os.path.basename(n)[:-5]] = json.loads(z.read(n))
    return out


def layer_bands():
    L = read_json(os.path.join(ROOT, 'kubejs/data/mythicbotany/libx/biome_layer/alfheim.json'))
    by = collections.defaultdict(list)
    for b in L['biomes']:
        by[b['biome']].append(b['parameters'])
    return by, len(L['biomes'])


# The Greatbole is not naturally placed. It has no structure set: gen_world_hub assembles it
# with `/place template` at a fixed origin, and `has_greatbole` names the WHOLE layer only so
# that the placement probe is never rejected on biome grounds. Listing it against all 25 biomes
# would read as "every biome can contain a Greatbole", which is the opposite of true.
COMMANDED = {'greatbole'}


def structures_by_biome():
    tags = {}
    for p in glob.glob(os.path.join(ROOT, 'kubejs/data/alfheim/tags/worldgen/biome/has_*.json')):
        tags[os.path.basename(p)[:-5]] = set(read_json(p)['values'])
    sets = {os.path.basename(p)[:-5] for p in
            glob.glob(os.path.join(ROOT, 'kubejs/data/alfheim/worldgen/structure_set/*.json'))}
    out = collections.defaultdict(list)
    for p in sorted(glob.glob(os.path.join(ROOT, 'kubejs/data/alfheim/worldgen/structure/*.json'))):
        sid = os.path.basename(p)[:-5]
        if sid in COMMANDED:
            continue
        b = read_json(p).get('biomes', '')
        if isinstance(b, str) and b.startswith('#'):
            names = tags.get(b.split(':')[-1], set())
        elif isinstance(b, list):
            names = set(b)
        else:
            names = {b}
        for n in names:
            out[n].append(sid)
    return out, sets


def deep_palettes():
    src = open(os.path.join(ROOT, 'tools/gen_deep_terrain.py'), encoding='utf-8').read()
    block = re.search(r'biome_palettes=\{(.*?)\n    \}', src, re.S).group(1)
    return {m.group(1): [x.strip().strip("'") for x in m.group(2).split(',')]
            for m in re.finditer(r"'([^']+)':\[([^\]]+)\]", block)}


def climate_facts():
    """Per axis: the vanilla noise, its base period, our scale and amplification."""
    z = client_jar()
    rows = []
    for axis, fn in CLIMATE_AXES:
        d = read_json(os.path.join(
            ROOT, 'kubejs/data/mythicbotany/worldgen/density_function', fn + '.json'))
        s = json.dumps(d)
        noise = re.search(r'"noise": "([^"]+)"', s).group(1)
        xz = float(re.search(r'"xz_scale": ([0-9.]+)', s).group(1))
        amp = re.search(r'"argument1": ([0-9.]+)', s)
        amp = float(amp.group(1)) if amp else 1.0
        base = None
        if z is not None:
            try:
                nd = json.loads(z.read(f'data/minecraft/worldgen/noise/{noise.split(":")[1]}.json'))
                base = 2 ** (-nd['firstOctave'])
            except KeyError:
                base = None
        rows.append({'axis': axis, 'noise': noise, 'base': base, 'xz': xz, 'amp': amp,
                     'region': (base / xz) if base else None})
    return rows


# --- rendering --------------------------------------------------------------------------------

def band_text(p):
    parts = []
    for a in AXES:
        lo, hi = p[a]
        if [lo, hi] != [-1.0, 1.0]:
            parts.append(f'`{AXIS_SHORT[a]}` {lo:g}‥{hi:g}')
    return ', '.join(parts) if parts else '*(everything left over)*'


def hexcol(v):
    return f'#{v:06X}' if isinstance(v, int) else str(v)


def render():
    biomes = load_biomes()
    bands, total_bands = layer_bands()
    structures, structure_sets = structures_by_biome()
    palettes = deep_palettes()
    climate = climate_facts()
    ns_settings = read_json(os.path.join(
        ROOT, 'kubejs/data/mythicbotany/worldgen/noise_settings/alfheim.json'))
    z = mb_jar()
    dim = json.loads(z.read('data/mythicbotany/dimension/alfheim.json'))
    dtype = json.loads(z.read('data/mythicbotany/dimension_type/alfheim.json'))

    ours = sorted(k for k in bands if k.startswith(f'{NS}:'))
    theirs = sorted(k for k in bands if not k.startswith(f'{NS}:'))

    L = []
    w = L.append
    w('# Alfheim Biome Index')
    w('')
    w('**Role:** Record document. The complete list of biomes that generate in '
      '`mythicbotany:alfheim`, the climate conditions that select each one, and the world '
      'parameters they generate under.')
    w('')
    w('**GENERATED by `tools/gen_biome_index.py` — do not hand-edit.** Every figure is read '
      'out of the shipping data: the emitted biome layer, the biome JSONs, MythicBotany\'s own '
      'five biomes inside its jar, the climate density functions, the structure biome tags and '
      'the deep geology table. Regenerate after any worldgen change:')
    w('')
    w('```')
    w('python tools/gen_biome_index.py')
    w('```')
    w('')
    w('**Authority:** subordinate to `INSTRUCTIONS.md`. Where this disagrees with the datapack, '
      'the datapack is right and this file is stale.')
    w('')
    w('---')
    w('')

    # ---- 1. the dimension
    w('## 1. The dimension')
    w('')
    w('| Fact | Value |')
    w('|---|---|')
    w(f'| Dimension | `mythicbotany:alfheim` — the mod\'s own, not an Overworld override |')
    w(f'| Generator | `{dim["generator"]["type"]}`, biome source '
      f'`{dim["generator"]["biome_source"]["type"]}` |')
    w(f'| Noise settings | `{dim["generator"].get("settings")}` |')
    w(f'| Biome layer | `mythicbotany/libx/biome_layer/alfheim.json` — **ours**, overriding '
      f'the mod\'s |')
    w(f'| Build limits | min_y **{dtype.get("min_y")}**, height **{dtype.get("height")}**, '
      f'logical height {dtype.get("logical_height")} |')
    w(f'| Sea level | **{ns_settings.get("sea_level")}** |')
    w(f'| Default block / fluid | `{ns_settings["default_block"]["Name"]}` / '
      f'`{ns_settings["default_fluid"]["Name"]}` |')
    w(f'| Aquifers / ore veins | {ns_settings.get("aquifers_enabled")} / '
      f'{ns_settings.get("ore_veins_enabled")} |')
    w(f'| Skylight / natural / bed works | {dtype.get("has_skylight")} / '
      f'{dtype.get("natural")} / {dtype.get("bed_works")} |')
    w(f'| Raids / piglin safe | {dtype.get("has_raids")} / {dtype.get("piglin_safe")} |')
    w(f'| Coordinate scale | {dtype.get("coordinate_scale")} |')
    w(f'| Ambient light / effects | {dtype.get("ambient_light")} / `{dtype.get("effects")}` |')
    w('')
    w('The dimension type is otherwise an Overworld clone; only `has_raids` differs. That is '
      'deliberate — see `INSTRUCTIONS.md` §1.')
    w('')

    # ---- 2. the climate axes
    w('## 2. The climate axes')
    w('')
    w('Biome selection is a nearest-match over five climate parameters. Four of them are '
      'produced by density functions **we override**; `erosion` is left as MythicBotany ships '
      'it. Each axis borrows a vanilla noise, and the size of the regions it produces is that '
      'noise\'s own base period divided by our `xz_scale`.')
    w('')
    w('| Axis | Vanilla noise | Base period | `xz_scale` | Amplified | Region produced |')
    w('|---|---|---:|---:|---:|---:|')
    for r in climate:
        base = f'{r["base"]:,} blk' if r['base'] else '—'
        region = f'**{r["region"]:,.0f} blk**' if r['region'] else '—'
        w(f'| {r["axis"]} | `{r["noise"]}` | {base} | {r["xz"]:g} | ×{r["amp"]:g} | {region} |')
    w('| erosion | *(MythicBotany\'s own, not overridden)* | — | — | — | — |')
    w('')
    w('The differing region sizes are intentional and nested: broad thermal zones, humidity '
      'variation inside them, weirdness variants inside that. One shared `xz_scale` across four '
      'noises whose base periods span a 16× range is what produced the 16,384-block temperature '
      'bands recorded in `BACKLOG.md` B-83, and B-84 is the correction.')
    w('')
    w(f'Amplification multiplies before a clamp to ±1, widening the tails so a band declared '
      f'near an extreme is reachable at all.')
    w('')

    # ---- 3. the index
    w('## 3. The index')
    w('')
    w(f'**{len(bands)} biomes** generate here, across **{total_bands} disjoint climate bands**. '
      f'{len(ours)} are ours; {len(theirs)} are MythicBotany\'s, kept because they carry the '
      f'mod\'s own identity where we have not claimed anything.')
    w('')
    w('A biome with several bands is one place selected by several disjoint climate boxes — the '
      'partition splits a claim wherever an earlier claim already took part of it. Bands are '
      'listed exactly as emitted.')
    w('')
    w('| Biome | Owner | Bands | Climate condition |')
    w('|---|---|---:|---|')
    for name in ours + theirs:
        owner = 'ours' if name.startswith(f'{NS}:') else 'MythicBotany'
        bs = bands[name]
        first = band_text(bs[0])
        w(f'| `{name}` | {owner} | {len(bs)} | {first} |')
        for extra in bs[1:]:
            w(f'| | | | {band_text(extra)} |')
    w('')

    # ---- 4. per-biome detail
    w('## 4. What each biome contains')
    w('')
    w('`Climate` is the biome\'s own temperature/downfall pair, which drives grass colour, '
      'rain and freezing — separate from the climate *parameters* in §3, which only decide '
      'where it is placed. `Deep geology` is the five-stone family the surface rules give its '
      'underground; the six Void biomes use the Void\'s own geology instead.')
    w('')
    for name in ours + theirs:
        d = biomes.get(name)
        if d is None:
            continue
        eff = d.get('effects', {})
        w(f'### `{name}`')
        w('')
        w(f'- **Climate** — temperature {d.get("temperature")}, downfall '
          f'{d.get("downfall")}, precipitation {d.get("has_precipitation")}'
          + (f', modifier `{d["temperature_modifier"]}`' if d.get('temperature_modifier') else ''))
        cols = ', '.join(f'{k.replace("_", " ")} `{hexcol(eff[k])}`'
                         for k in ('sky_color', 'fog_color', 'water_color', 'water_fog_color')
                         if k in eff)
        w(f'- **Colours** — {cols}')
        if 'particle' in eff:
            pt = eff['particle']
            w(f'- **Particle** — `{pt["options"]["type"]}` at probability {pt["probability"]}')
        feats = d.get('features', [])
        listed = [(STEPS[i] if i < len(STEPS) else f'step {i}', f)
                  for i, f in enumerate(feats) if f]
        if listed:
            w('- **Features**')
            for step, f in listed:
                if step == 'underground_ores':
                    w(f'    - `{step}` — {len(f)} ore/stone features '
                      f'(the shared Alfheim ore column)')
                else:
                    w(f'    - `{step}` — ' + ', '.join(f'`{x}`' for x in f))
        else:
            w('- **Features** — none')
        sp = {k: v for k, v in d.get('spawners', {}).items() if v}
        if sp:
            parts = []
            for cat, mobs in sorted(sp.items()):
                ids = ', '.join(f'`{m["type"]}`' for m in mobs)
                parts.append(f'*{cat}* — {ids}')
            w('- **Spawns** — ' + '; '.join(parts))
        else:
            w('- **Spawns** — none')
        st = structures.get(name, [])
        w('- **Structures** — ' + (', '.join(f'`{s}`' for s in sorted(st)) if st else 'none'))
        pal = palettes.get(name)
        w('- **Deep geology** — ' + (', '.join(f'`{p}`' for p in pal) if pal
                                     else "the Void geology (no five-stone family)"))
        w('')

    # ---- 5. coverage
    #
    # An index that only lists is worth less than one that measures. These are computed from the
    # same data as the rest of the file, so they cannot go stale while the file says they are
    # fine. "Thin" is the state Infested Warren and Decayed Mire were in when the 2026-09-07
    # field review reported them reading as "gently rolling hills": a colour palette, a mob list
    # and nothing on the ground.
    w('## 5. Coverage')
    w('')
    w('Computed, not asserted. The Void biomes are exempt from vegetation by doctrine — '
      '"nothing grows" is absolute there — so they are counted separately rather than flagged.')
    w('')
    bare, thin, nostruct, nogeo = [], [], [], []
    for name in ours + theirs:
        d = biomes.get(name)
        if d is None:
            continue
        void = name.split(':')[-1] in VOID_BIOMES
        feats = d.get('features', [])
        veg = feats[9] if len(feats) > 9 else []
        if not void:
            if not veg:
                bare.append(name)
            elif len(veg) <= 1:
                thin.append(name)
            if name not in palettes:
                nogeo.append(name)
        if not structures.get(name):
            nostruct.append(name)
    w(f'- **Land biomes with no vegetal decoration at all:** '
      + (', '.join(f'`{n}`' for n in bare) if bare else '*none*'))
    w(f'- **Land biomes with a single vegetal feature:** '
      + (', '.join(f'`{n}`' for n in thin) if thin else '*none*'))
    w(f'- **Biomes with no natural structure:** '
      + (', '.join(f'`{n}`' for n in nostruct) if nostruct else '*none*'))
    w(f'- **Land biomes with no five-stone deep geology:** '
      + (', '.join(f'`{n}`' for n in nogeo) if nogeo else '*none*'))
    w(f'- **Void biomes (vegetation intentionally absent):** '
      + ', '.join(f'`{n}`' for n in sorted(ours + theirs)
                  if n.split(':')[-1] in VOID_BIOMES))
    w('')

    w('---')
    w('')
    w(f'Generated from {len(bands)} biomes, {total_bands} layer bands, '
      f'{sum(len(v) for v in structures.values())} biome-structure assignments and '
      f'{len(palettes)} deep geology families.')
    return '\n'.join(L) + '\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true',
                    help='exit 1 if the checked-in index is stale')
    a = ap.parse_args()
    text = render()
    if a.check:
        if not os.path.exists(OUT):
            print(f'!! {OUT} does not exist; run tools/gen_biome_index.py')
            return 1
        current = open(OUT, encoding='utf-8').read()
        if current != text:
            print(f'!! {os.path.relpath(OUT, ROOT)} is stale; run tools/gen_biome_index.py')
            return 1
        print(f'PASS: {os.path.relpath(OUT, ROOT)} matches the shipping worldgen data')
        return 0
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    print(f'wrote {os.path.relpath(OUT, ROOT)} ({len(text):,} bytes)')
    return 0


if __name__ == '__main__':
    sys.exit(main())

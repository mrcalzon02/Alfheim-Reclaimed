# Seasonal pixie sky-island settlements

**Status:** direct runtime assembly proven, 2026-09-07. Natural-placement census, spawner activation
and client visual review remain.

## Decision: the centre is a dew well

Every village is organized around a tiny public **dew well**. This is better than a town hall,
church or ordinary village well for three reasons:

1. it is civic without making pixies behave like miniature humans;
2. it gives every culture the same readable jigsaw hub while allowing four strong seasonal forms;
3. its basin and service hatch naturally conceal the required spawner vault directly beneath it.

The four centres are related, not identical:

| Court | Centre | Cultural reading |
|---|---|---|
| Spring | Bloom-canopied rain catcher | play, courtship, germination and shared water |
| Summer | Golden sunwell and honey pavilion | status, warmth, bees and the Golden Seelie Court |
| Autumn | Hay-roofed cider/harvest cistern | gathering, storage and preparation for winter |
| Winter | Blue-ice moonwell with a soul light | memory, stillness and the Winter Court's soul imagery |

The spawner is not exposed inside the basin. It sits in a 5×5 Livingrock vault below the centre,
bounded to one pixie at a time and four nearby pixies. An open side hatch and ladder behind the well
make the vault serviceable and give spawned flying pixies a route to the settlement. The machinery
is therefore hidden during ordinary arrival but not sealed into an unmaintainable black box.

## Settlement grammar

Each settlement starts with one 33×33 organic floating island at absolute Y 208. The underside
tapers, carries asymmetrical stone/root pendants and never fills its square bounding corners. The
island owns six upward jigsaw sockets:

- one fixed seasonal dew well;
- three houses chosen independently from four miniature forms;
- one functional irrigated vanilla garden;
- one complete matching Feywild tree and a spare sapling.

This is a one-step jigsaw, intentionally. A recursive road village would either exceed the small
island or create unsupported pieces. Keeping the landform in the start piece guarantees that every
child has authored support and that the village still reads as a floating island from below.

## The four cultures

| Pixie | Host biomes | Tree | Vanilla food plot | Architectural character |
|---|---|---|---|---|
| Spring | Bloomfall Vale, Alfheim Plains | Spring tree | carrots and beetroot | flowering canopy, moss and playful lofts |
| Summer | Golden Fields | Summer tree | wheat and melons | gold/honey accents and a formal pavilion |
| Autumn | Ashen Grove, Silverbark Wood | Autumn tree | potatoes and pumpkins | hay, mud brick and harvest stores |
| Winter | Starved Reach, Alfheim Hills | Winter tree | potatoes and beetroot in a glass coldframe | blue ice, soul lights and sparse roofs |

The MythicBotany alf pixie is not a fifth culture. Feywild supplies a complete four-part set of
seasonal pixies, trees, timber and courts; the alf pixie has no corresponding material culture.
It remains valid ambient Alfheim wildlife rather than receiving a mismatched settlement.

## Placement and collision contract

Each culture uses its own biome tag, structure and stable salted random-spread set. Spacing 56 and
separation 24 make settlements discoveries rather than skyline clutter. Terrain adaptation is
`none`, no heightmap projection is used, and all pieces use rigid projection so the island cannot
be pulled down onto terrain. Continuity Works currently auto-enrols every registered structure,
including these four, in its 500-block structure exclusion system. That supplies strong major-
structure clearance but may make the effective distribution much rarer than the structure-set
spacing alone implies.

The direct runtime assembly proof bypassed normal structure competition. A natural fresh-world
census must therefore measure both occurrence and clearance before the present protection policy
is accepted. The authored jigsaw pieces do not intersect one another; if the census finds the
hamlets over-suppressed or colliding, solve that in placement/exclusion policy rather than by
flattening or shrinking the islands.

## Runtime evidence

Forge accepted all four structures and directly assembled one of each in
`validation-pixie-assembly-0907b` at Y 208. The saved-region audit found the centre, three houses,
garden and seasonal tree at every site, no lingering jigsaw blocks, and exactly one correctly typed
bounded pixie spawner beneath each centre. Startup completed with all 17 startup and 26 server
scripts clean, and the server saved and stopped normally.

## Acceptance still required

- Each culture places at least once in a fresh world and nowhere outside its host biome tag.
- Pixies spawn in the buried vault, can fly out through the service shaft, and respect the cap.
- Crops remain planted and renewable; the winter coldframe is sufficiently lit.
- From ground level and from below, the silhouette reads as a small floating landform.
- A client pass checks house scale, path legibility, fall hazards and major-structure clearance.

Source: `tools/gen_pixie_settlements.py`. Static checker: `tools/check_pixie_settlements.py`.
Saved-world checker: `tools/check_pixie_runtime.py`. Direct assembly harness:
`tools/run_server.py --pixie-only`.

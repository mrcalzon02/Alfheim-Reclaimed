# Coordinated upper-rock and dungeon reservations

## Cause and ownership

The prior upper-rock adapter reserved an 800-block square around every potentially
eligible underground set candidate. Archaeology uses a 48-chunk grid, ley corridors
a 40-chunk grid, and Andwari caves a 28-chunk grid. Their combined reservations
covered all sampled discovery sites. Andwari's actual biome tag contains only
Golden Fields, but the previous possible-biome test reserved that set everywhere
in the dimension. The baseline survey rejected 256 candidates; a generic eligibility
experiment rejected another 143 while adding unnecessary work.

The fix changes only the pack-owned structure adapters and definitions. MythicBotany's
Andwari definition, placement, tags and jar remain unchanged. Broad density/surface
terrain, bedrock, all structure templates, and player saves remain unchanged.

## Shared, deterministic allocation

Upper discoveries retain their original 80/48-chunk grid and salt 202610151.
`UndergroundAllocation.selected` hashes seed and signed grid cell to select a nominal
one in four candidates, outside the existing 4,000-block origin exclusion. There
is no retry, region search, mutable reservation cache or fallback family. Eligibility
and terrain checks can still reject a selected site.

The pack-owned Deep Quarry, Elder Kings Tomb, Faultwork, their matching headworks,
and ley corridors use `AllocatedUndergroundStructure`, a wrapper around their
unchanged vanilla jigsaw layouts. Before any terrain sampling or piece assembly,
the wrapper checks nine upper-grid candidates in neighboring cells. If a selected
discovery candidate is within 800 blocks on both axes, the pack dungeon yields.
Headworks and their buried complexes make the same decision at their shared grid
position, preserving their existing co-location contract. Existing grids, weights,
depth bands, pools, sockets and authored details are preserved.

An upper discovery skips reservations from these cooperating adapters. It still
protects winning district reservations and other biome-eligible underground sets.
Only the verified Andwari vanilla-jigsaw set receives actual start/biome eligibility
checks. Those inspect nearby generation stubs without invoking the lazy piece
builder, modifying Andwari, loading chunks or searching for replacement sites.
This scoped check runs only for the sparse selected discovery candidates; the
unsuccessful generic dungeon eligibility experiment is not restored.

The 800-block axis distance conservatively leaves at least **593 blocks** between
the new 15-block-radius discovery and a pack dungeon reservation of radius 192
(128-block jigsaw reach plus root offset allowance). New discovery candidates
themselves have at least 738 blocks between footprints. The tests cover negative
coordinates, stable selection, selection rate, boundary distances and completeness
of the nine-cell search. The static gate checks all managed reaches remain <=128.
This is a contract for this underground allocation and the previously protected
districts; it does not establish a universal spacing guarantee for every unrelated
surface feature or future non-random structure placement.

Reserved sites may remain empty after terrain, biome or other exclusion rejection.
This deliberately bounds work and avoids generation-order dependencies. The new
discovery family remains sparse; a small test is not a density or gameplay acceptance.

## Verification and limits

`tools/check_underground_allocation.py` verifies the five native definitions preserve
their vanilla layouts, placement constants match, and headworks share their complex
grid. It reads the actual installed Andwari definition/tag, records its jar hash,
and invokes Continuity Works 0.3.2 `StructureCapability.audit` for all twelve existing
upper-rock templates. `tools/underground_allocation_report.json` records the results
and installed first-party jar hash. Java17 build and 64 tests pass. Archaeology and
ley-line source-to-shipping checks pass, the 39-file terrain/106-model guard passes,
and the feature-order checker reports zero cycles.

The repaired bounded survey on seed 3536368297089363045 admits four sites from
205 candidates reached within four diagnostic time budgets. See
`tools/upper_natural_runtime_report.json` for exact positions, summaries and the
tested artifact hash. `tools/run_upper_natural_validation.py populate` loads at most
three 5x5-chunk sites and checks saved native starts plus template block samples;
its final report determines whether natural placement passed. A survey alone is
not saved-world placement proof. Client visuals and broader density review remain
separate gates.

The population check now passes: three naturally generated saved starts at
[10673,82,9393], [-7599,38,5441] and [5281,36,-12415]. Two are Basalt Columns and
one is Moss Grotto. Their original surveyed origins and bounds agree exactly;
905 of 909 sampled solid blocks match (the moss site has four decoration changes).
No `/place structure` or `/place template` commands were used. Both runs stopped
cleanly with the same installed jar hash. The population console is
`server/console-20261015-155542.log`. This is scoped natural placement acceptance,
not client visual, population density or universal surface-structure spacing acceptance.

This policy governs future generation. Dungeons already generated under older
rules have not yielded a reservation retroactively. Mixed old/new generation
boundaries and previously placed structures require a separate saved-world audit;
no player-world relocation or rewriting is included.

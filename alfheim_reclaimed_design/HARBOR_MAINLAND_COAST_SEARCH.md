# Mainland coast survey and low-bank repair - 2026-10-13

The harbor remains the active structure-development target. Natural generation
is withheld: none of the newly checked sites supports its entire footprint.
The repaired broad terrain generator was not changed.

Read-only surveys measured 461,568 saved columns in the bounded field-review
world and 194,816 in the central field-review world, both on seed
3536368297089363045. The saved-data screen now mirrors selectable quay heights,
supported shallow reclamation and the mandatory dry approach. It skips empty
region placeholders and applies the old roads-fixture exclusion only to that save.
These heightmaps include decoration, so they select candidates rather than prove
native terrain fit. The surveys do not modify either world.

The first four native checks found an unnecessarily strict lower bound: the
Sporebank site at origin (720,544) contains dry first-free surface heights 61 and
63, despite the architecture's solid footing reaching Y=58. Requiring dry land
to begin at sea level rejected this supported low bank. The lower bound now
follows the actual lowest footing, sea level -6. Waterline, seabed depth, upper
relief, every-column checking and mandatory dry connections remain enforced.

Java 17 build and nine policy tests passed. The new test admits dry first-free
heights 58/61/63, rejects height 57 and detects a single unsupported low column
between coarse probes. The rebuilt first-party companion is installed; its prior
version is retained in `quarantine/first-party-harbor-low-bank-20261013/`.
Third-party jars were not edited.

Ten candidates then received fresh native-generator audits. Five were in eligible
shore biomes; none passed the complete footprint. All sampled height values
matched Minecraft's height methods. Rejection checks took 70-848 ms; this does
not measure the cost of a successful complete harbor. At (720,544), the repaired
policy examined 60 distinct columns instead of the previous 7 before rejection,
showing that it passed the former low-bank obstacle and reached later checks.

Evidence: `tools/harbor_mainland_native_survey.json` for the original four checks,
`tools/harbor_low_bank_native_survey.json` for the repaired ten-site checks,
and `server/console-20261013-103031.log`. Server and validation harness exited 0.
The 45 harbor resource files still reproduce from source, with ten architecture
members, nine supported ports, 72 cultural modules, contained basins and supported
lighthouse circulation. The protected 39 terrain files remain unchanged.

No harbor was forced into a rejected site. Prior raised-bank assembly evidence
remains separate from natural-coast admission. Player saves were not edited.

Next work: use the measured coasts to investigate smaller or terraced harbor
arrangements and broader representative shoreline coverage. Keep foundation
reach and deep-water rejection intact. A full native placement, successful-path
cost, decoration compatibility and client visual fit still precede admission.

# Bounded, approximate harbor placement - 2026-10-13

The user accepts imperfect harbor fit and explicitly prefers moving on to more
structure development. Natural generation is now enabled sparsely, with one
candidate per 80x80-chunk region before biome and anchor rejection; separation is
48 chunks. Only Tidewood Shore, Mistbark Shore and Sporebank Shore are eligible.
New eligible chunks can produce harbors after the updated instance is loaded;
existing chunks are not rebuilt.

Natural placement reads representative shore anchors and one center per member.
It tolerates local gaps and clipping. Anchors require shallow dock water and dry
exchange/approach ground; center checks reject gross void/deep-ocean/cliff sites.
The unchanged ten-member architecture and matched raised foundations are used.

One shared budget covers all orientations: at most 32 distinct native columns,
with a 150 ms stop deadline. There is no dense scan or exhaustive fallback.
Expired attempts are skipped. The deadline is checked before and after each
native call; an in-progress call may overrun it, but no further call starts.
This is a stop budget, not engine preemption or an exact wall-clock guarantee.

Twenty policy tests and the Java 17 build passed, including column limits,
expired/slow-call behavior, deliberate acceptance of unsampled imperfections
in all orientations, and gross-void rejection. Forty-six harbor resources pass
source equality; the installed first-party jar hash matches the build. Its prior
version is retained under `quarantine/first-party-harbor-bounded-20261013/`.

`audit_bounded` reports this policy. Strict audits and `place_checked` remain
manual tools; natural generation uses the bounded path. Debug timing includes
two independent height-parity checks that natural generation does not perform.

The live smoke test now passes after approval service availability returned.
Seven native-site audits used 4-17 distinct columns and took 64-149 ms including
debug height checks. Three eligible shore sites were accepted; unsuitable anchors
and a deep ocean case were skipped. These are sample timings, not a universal
wall-clock guarantee. The 32-column/150 ms stop policy remains unchanged.

The actual structure command then placed the full harbor on an unmodified
Sporebank coast. All ten members, nine supported connections, authored air,
cultural fixtures and added foundation segments passed saved-world verification.
No artificial coast or terrain infill fixture was used for that placement.
Evidence: `tools/harbor_bounded_runtime.json`,
`tools/harbor_complex_runtime_census.json` and
`server/console-20261013-155051.log`. Server and harness exited 0.

Geometric perfection is deferred by user direction. Placement frequency and
client visual review remain pending without blocking Sacred Precinct source
development. All 39 protected terrain files, 103-model geometry and field repairs
pass; feature ordering has zero cycles. Player saves and third-party jars were
not edited.

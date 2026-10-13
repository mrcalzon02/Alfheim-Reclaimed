# Harbor shoreline placement guard

The first-party companion now provides `alfheim_companion:shoreline_harbor`.
The harbor's registered structure uses that type with `terrain_adaptation: none`.
The guard reads terrain and rejects unsuitable sites; it does not reshape terrain.
Natural random-spread placement remains withheld until a real generated coast and
generation cost have been verified.

One policy serves both the natural-generation adapter and operator checked
placement. It considers all four rotations, with the pier and drydock facing
water. Fast probes reject obvious failures before a coarse scan; a successful
candidate then checks every column of every member's actual footprint. A narrow
ravine, hidden cliff or unloaded column cannot pass between sample points.

The quay begins at sea level +2 and can rise another 2/4/6 blocks when matched
foundation segments are placed below every member. All choices keep the lowest
footing at sea level -6. Away from the shore apron, pier/drydock columns must have
water at sea level -1, a clear waterline and a seabed within that footing reach.
The Z=-16 through Z=15 apron can mix supported shallows and ground. Occupied
platforms may also reclaim equally supported shallows. Dry ground is limited to
sea level -6 through sea level +3 + the chosen lift, so supported low dry banks
are admitted without extending the actual foundation reach. Dry exchange-center and inland
approach probes remain mandatory. Missing columns, deep water and excessive
relief are rejected; the additional foundation geometry is not a waived check.

`HarborGeometry.java` contains the exact ten-member origins, rotations and bounds
derived from `tools/harbor_complex_layout.json`. `tools/check_harbor_guard.py`
checks equality, the guarded structure type, disabled terrain adjustment,
absence of a natural placement set, policy tests and the installed jar hash.

Operator commands, in `mythicbotany:alfheim`:

```text
alfheimharbor audit <x> <z>
alfheimharbor audit_generated <x> <z>
alfheimharbor place_checked <x> <z>
```

Coordinates are the proposed template origin, not its center. Both audits are read-only. The generated-terrain audit reports native fit, biome
eligibility, sampled columns, height-method parity and elapsed time; it does not
require loading or changing the requested terrain.
Placement requires operator permission and accepts only a fully loaded footprint
that passes the same shoreline policy. It constructs the ten rigid members in
the accepted orientation using the standard template/pool placement machinery.
The natural-generation adapter samples generated terrain instead of loaded blocks.

Java 17 compilation and the existing companion test suite passed. Fifteen
policy tests cover all rotations, inland/open-ocean rejection, deep water,
excessive relief, missing columns and single-column hazards between coarse probes,
curved shore acceptance, deep/blocked apron rejection, raised footers, mandatory
dry approaches and low dry banks bounded by actual footing reach. Additional
tests exercise the read-only proposed footprints and their retained hazards;
see `HARBOR_FOOTPRINT_COMPARISON.md`. Proposals have no placement path.
The prior companion jar is preserved under
`quarantine/first-party-harbor-guard-20261012/`; hashes are recorded in
`tools/harbor_guard_build.json`. Third-party jars were not edited.

The live test uses only `server/validation-harbor-guard-20261012`. Its synthetic
coast is modified explicitly for validation. Earlier fixtures were rejected for
an unreachable seabed and a dirt cap above the waterline; both were corrected
without weakening the policy. A high-column rejection and a complete checked
placement are required before acceptance. The final run passed: the coast was accepted at quay Y=66 with rotation 0;
a single-column cliff was rejected; checked placement retained all ten members,
nine supported joins, 72 furnishings and 345,003 authored air cells.
`server/console-20261012-201303.log` saved all dimensions; server and harness exited 0.
Live evidence: `tools/harbor_guard_runtime.json`.

Remaining admission gates: a real generated shoreline, native generation
performance, decoration compatibility, client visual terrain fit and natural
placement frequency. The synthetic test cannot establish those gates.

Native coast findings and timing scope: `HARBOR_REAL_COAST_VALIDATION.md`. The
current flat footprint has not passed a real-coast fit case; natural placement
remains withheld while the harbor is repaired.

Adaptation and raised-bank runtime evidence: `HARBOR_ADAPTIVE_QUAY.md`. Reclaimed
occupied platforms may stand over supported shallow water. Dry exchange-center
and inland approach probes remain required; unsupported/deep-water sites still fail.

Progressive refinement and paired rejection timings: `HARBOR_REFINEMENT_2026-10-13.md`.
Successful candidates still check every footprint column; depth/height limits are unchanged.

# Harbor terrain-check refinement - 2026-10-13

The required-core checker now refines its sampling across the district at spacing
8, 4, 2 and finally 1. Previously it jumped from spacing 8 to a complete walk
through each member. Intermediate passes find smaller hazards before paying for
many unrelated native columns. Values remain cached within each audit, and a
successful check still visits every footprint column. No support, waterline,
orientation or height limit changed.

The paired native comparison retained the same seed, five origins and core
footprint. Every acceptance decision and biome eligibility result stayed equal.
All five sites remain rejected. The independently sampled height-method parity
checks passed.

| Origin X,Z | Distinct columns before / after | Time before / after |
|---|---:|---:|
| -1548,612 | 8 / 8 | 140 / 150 ms |
| -1528,616 | 9 / 9 | 151 / 154 ms |
| -1552,544 | 20 / 20 | 226 / 229 ms |
| 704,544 | 2523 / 1003 | 17734 / 7361 ms |
| 720,544 | 156 / 156 | 1177 / 1219 ms |

The previously slow Sporebank case used 60% fewer distinct native columns and
took 58% less time in this paired run. Small early-rejection cases have unchanged
column counts and variable timings. This is a measured late-rejection improvement,
not a successful-path generation benchmark. A 7.4-second rejection still fails the
performance goal for automatic generation.

Diagnostics now record the final sampled column for each rejected orientation
and quay height. The validation tool maps those coordinates back to the proposed
member and labels the violated constraint. At Sporebank origin (704,544), rotation
3 and lift 6, the first remaining failure is world (708,491), local (53,4), inside
the harbormaster house. The water surface is 64 and the seabed first-free height
is 57; the current lowest footing is 58. Other recorded failures include exchange
land at height 75, an exchange water pocket with seabed 51, and approach land at
height 76. These require different physical responses and are not interchangeable
reasons to loosen a global limit.

An existing solid 39x47x2 footer was checked as a bounded support option for that
first harbormaster failure. Its 3,666 distinct source cells are all solid. At
proposed origin (708,56,451), rotation 0, it spans the gap and contacts the known
ground beneath (708,491), extending only that member's footing from 58 to 56.
This source option is recorded in `tools/harbor_support_gap_plan.json`. It has not
been placed or admitted into the policy, and later hazards may remain. The core's
furnished templates and unused-branch closures also still need authoring.

Java 17 build and fifteen policy tests passed. The added tests verify earlier
intermediate-grid rejection, complete coverage of successful footprints and exact
reporting of an odd-coordinate hazard missed by coarser grids. Existing rotation,
depth, void, cliff, low-bank and proposed-core tests remain passing. The rebuilt
first-party companion is installed, with its predecessor preserved under
`quarantine/first-party-harbor-refinement-20261013/`.

Runtime evidence: `tools/harbor_refinement_native_validation.json` and
`server/console-20261013-141947.log`. Server and validation harness exited 0.
The comparison retains the previous core evidence separately. The 39 protected
broad terrain files remain unchanged, and the 103-model and field-repair checks
pass. No player save, third-party jar or furnished harbor template was edited.

Next: pair member-specific support construction with its actual reach checks,
verify remaining core columns, and improve the late/successful sampling path.
Then author and verify the core with safe closures and optional satellites.
Natural generation remains disabled until native placement, performance and
client visual fit pass.

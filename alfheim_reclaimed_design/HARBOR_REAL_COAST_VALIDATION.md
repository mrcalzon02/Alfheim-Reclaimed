# Harbor real-coast validation - 2026-10-12

The current flat harbor has not passed a real-coast fit case. Natural generation
remains withheld; the harbor layout and foundations remain the repair target.
Broad terrain generation and player saves were not modified.

The read-only saved-world survey covered 1,370 chunks and 350,720 columns on seed
3536368297089363045, excluding the hub and manually placed test footprint. There
were 19,191 shallow-water columns and 92 coarse shoreline orientations. The initial
decorated-heightmap screen rejected 91 for land height/support and one for missing
saved columns. These maps include trees and other decoration and are not a substitute
for native generation checks. Evidence: `tools/harbor_saved_coast_survey.json`.

Native audits sampled 21 distinct sites, including 12 in eligible harbor biomes.
All rejected the initial policy. Review of the guard also exposed an unnecessarily rigid
seam requirement: the whole pier had to be wet immediately beside a completely
dry quay, effectively demanding a straight one-block shoreline transition.

The guard now permits a supported shore apron over the local Z=-16 through Z=15
band. This permits dry ground or shallow water near the shoreline, with the same
foundation reach, waterline and relief limits. Beyond it, the dock must remain
wet and occupied land dry. Inland/open-ocean sites still fail the wet/dry probes.
Six policy tests pass, including a curved shore and deep-water/blocked-waterline
apron rejection. The rule does not permit unsupported overhangs or deep water.

Four eligible Mistbark sites were rechecked on the native generator after this
correction. All still rejected. These are sampled results, not proof that no
possible coast exists anywhere in the world. The current footprint's fit remains
unproven and should be adapted using further height/depth profiles rather than
changing broad terrain or removing support checks.

The native sampler now derives surface and seabed heights from one generated
column instead of repeating three column calculations. Each live audit compared
up to eight sampled columns with Minecraft's independent height methods; parity
passed throughout. The initial 21-site measurements were 137-337 ms, median 159 ms.
The four apron rechecks were 191-242 ms. These timings include parity checks and
measure early rejection only. Complete successful-footprint validation and actual
natural placement cost remain unmeasured.

Evidence:

- Before apron: `tools/harbor_native_coast_survey_before_apron.json`, console
  `server/console-20261012-232603.log`.
- After apron: `tools/harbor_native_coast_survey.json`, console
  `server/console-20261012-234237.log`.
- Both dedicated survey servers saved and exited 0, without coastal fixture fills
  or harbor placement commands. Natural placement sets remain absent.
- First-party builds/tests, installed artifact hash and all 39 protected terrain
  file checks passed. Prior jars are preserved in the harbor-specific quarantine
  directories recorded by `tools/harbor_guard_build.json`.

Tooling: `survey_saved_harbor_coasts.py`, `run_harbor_native_survey.py`, and the
read-only operator command `alfheimharbor audit_generated <x> <z>`.

Next: profile the failed columns, adapt the harbor's stepped layout/foundations,
find a safe real-coast case, validate the full placed assembly and its generation
cost, then complete client visual terrain-fit review before natural admission.

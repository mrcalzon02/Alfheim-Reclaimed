# Custom biome feature coverage

Configuration audit, 2026-10-13. Includes jar defaults, datapack overrides and Forge feature modifiers. Counts are distinct features and first-party structures, not observed density. Controlled-only assemblies do not generate naturally.

| Biome | Vegetation features | Surface detail features | Natural structures | Controlled-only structures |
|---|---:|---:|---:|---:|
| alfheim:alfheim_ocean | 5 | 4 | 7 | 1 |
| alfheim:ashen_grove | 8 | 6 | 16 | 4 |
| alfheim:bloomfall_vale | 8 | 5 | 16 | 4 |
| alfheim:decayed_mire | 5 | 6 | 15 | 4 |
| alfheim:hollow_marches | 6 | 6 | 15 | 4 |
| alfheim:infested_warren | 6 | 5 | 15 | 4 |
| alfheim:mana_fen | 4 | 6 | 15 | 4 |
| alfheim:mistbark_shore | 5 | 4 | 8 | 1 |
| alfheim:prism_drift | 1 | 1 | 2 | 1 |
| alfheim:rootfall | 1 | 1 | 2 | 1 |
| alfheim:scorchfell | 3 | 5 | 15 | 4 |
| alfheim:sepulchral_reach | 1 | 1 | 2 | 1 |
| alfheim:shatterfields | 1 | 1 | 2 | 1 |
| alfheim:silverbark_wood | 7 | 5 | 16 | 4 |
| alfheim:sporebank_shore | 6 | 4 | 8 | 1 |
| alfheim:starless_reach | 1 | 1 | 2 | 1 |
| alfheim:starved_reach | 4 | 5 | 16 | 4 |
| alfheim:sundered_highlands | 6 | 5 | 15 | 4 |
| alfheim:tidewood_shore | 6 | 4 | 8 | 1 |
| alfheim:void_shore | 4 | 4 | 9 | 1 |
| alfheim:void_verge | 3 | 2 | 4 | 1 |
| mythicbotany:alfheim_hills | 5 | 7 | 16 | 4 |
| mythicbotany:alfheim_lakes | 4 | 5 | 7 | 1 |
| mythicbotany:alfheim_plains | 5 | 6 | 16 | 4 |
| mythicbotany:dreamwood_forest | 5 | 6 | 15 | 4 |
| mythicbotany:golden_fields | 4 | 6 | 17 | 4 |

No vegetation configured: none.

Only generic mystical flowers in the vegetation step: alfheim:prism_drift, alfheim:rootfall, alfheim:sepulchral_reach, alfheim:shatterfields, alfheim:starless_reach. This is sparse vegetation, not missing overall feature coverage. The earlier table omitted the local-modifications stage. These five regions already have distinct geological detail features, confirmed in the effective Forge feature lists. All eleven generation stages are now listed in the JSON audit. No duplicate geology or broad terrain changes were needed.

Void identities: Shatterfields anchor needles, Prism Drift crystal crowns, Rootfall fossil root aprons, Sepulchral Reach mourning steles, and Starless Reach astralite flecks. Source registration alone does not establish their natural success rate or visual quality; controlled placement evidence is recorded separately.

Void Shore and Void Verge both receive bramble and thorn patches plus Thorn Gate and Shore Memorial Court. Their substrate filter now includes their actual chalk/shale/sand/gravel surfaces. This corrects a placement blocker; it does not establish final natural density.

Broad density, noise, biome selection and surface rules are unchanged. See tools/biome_feature_coverage.json for exact feature and structure IDs.

## Observed void undergrowth

Fresh test world `validation-military-warden-20261013`: 64 sampled natural chunks. These counts include naturally placed undergrowth and any natural court plants; controlled pads are outside this sample.

| Biome | Plant | Saved blocks |
|---|---|---:|
| alfheim:alfheim_ocean | alfheim:bramble | 2 |
| alfheim:alfheim_ocean | mmorpg:thorn_bush | 9 |
| alfheim:void_shore | alfheim:bramble | 352 |
| alfheim:void_shore | mmorpg:thorn_bush | 319 |
| alfheim:void_verge | alfheim:bramble | 89 |
| alfheim:void_verge | mmorpg:thorn_bush | 106 |

Both plant types also survived the controlled chalk, shale, sand and gravel tests after block updates. A few plants cross the adjoining ocean biome boundary within patch spread. This local sample proves generation works; it does not establish final visual density or populate existing chunks.

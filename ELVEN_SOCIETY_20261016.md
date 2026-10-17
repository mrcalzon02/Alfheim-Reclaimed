# Elven society appearances — 2026-10-16

Twelve adult civilian roles: serf, servant, steward, artisan, nobleman,
noblewoman, lord, lady, prince, princess, king and queen. Each has four named
appearance selections in Spawn Eggs, with a matching modeled head item.
These are 48 appearances of one passive citizen entity, not 48 separate species.

The slim PlayerModel rig and six identity skins come from the installed
Rich's Races wood elves. Existing pack overrides for the Magister and Captain
remain active. Original faces, hair, garment patterns, gradients and outer
skin layers are rendered directly from those resource locations. The rejected
flat clothing replacement has been removed. No third-party jar was modified.

An independent animated model layer adds upward-sweeping ears, hats, crowns,
capes, split coat tails, tiered skirts, pleats, puffed sleeves, cuffs, collars
and lapels according to role. Added fabric derives its shading and motifs from
the corresponding supplied skin; role dyes and embroidery add variation.
Ear tones are sampled from that skin's face. The fourth noble/royal appearance
reuses the first identity with different finery; it is not a fourth new face.

Citizens wander, look around and flee danger. Their stored role and appearance
survive saving. They have no combat targets, recruitment, trading, court quests
or automatic world population in this change. Existing companion and court
entities remain separate.

Validation: Java 17 build and 71 tests; generated-resource checks; all packaged
asset/data bytes equal source. `tools/run_elven_society_validation.py` checks 48
actual spawn-item uses and 48 saved identity round trips in a disposable world.
Runtime evidence is recorded in `tools/elven_society_build.json` upon success.
Review sheets and front/side/back details are offline renders of baked geometry,
not game screenshots. Client motion and lighting review remains pending.
Restart Minecraft to load the installed companion jar.

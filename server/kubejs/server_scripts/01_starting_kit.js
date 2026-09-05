// Alfheim Reclaimed — starting kit
//
// Why this exists: Botania's `spawnWithLexicon` lives under [gardenOfGlass] and only fires in
// Garden of Glass worlds, so a normal world hands the player no Lexica Botania at all. Botania is
// the core of this pack, so that has to be fixed here. FTB Quests likewise does not give its book
// out on its own.
//
// Ars Nouveau (`spawnBook = true`) and Feywild give their own books already — they are listed in
// REFERENCE below but deliberately not granted again here.
//
// Runs once per player, guarded by a flag in persistent data so re-logging does not re-issue it.

const STARTING_KIT = [
    'botania:lexicon',   // Lexica Botania — the pack's core progression book
    'ftbquests:book',    // Quest Book — Magister Velrous's voice

    // B-46 — the petal safety net. Mystical flowers now generate in Alfheim (see
    // kubejs/data/botania/tags/worldgen/biome/mystical_flower_spawnlist.json), but petals
    // gate the Pure Daisy, the Petal Apothecary, the Wand of the Forest, the Mana Spreader
    // and every Rite — that is the whole Spine of Leaf on one reagent. A player who spawns
    // in the Ashen Grove, which is deliberately flowerless, must never be stranded.
    //
    // Two Floral Fertilizer is the *renewable* route, not the end product: applied to grass
    // it spawns mystical flowers. Era I Guides teach that it is craftable from bone meal and
    // four dyes, so the kit bootstraps the loop rather than replacing it.
    ['botania:fertilizer', 2],
    ['botania:white_petal', 4]
]

// Given automatically by their own mods; do not duplicate:
//   ars_nouveau:worn_notebook   (config/ars_nouveau-common.toml -> spawnBook = true)
//   feywild:feywild_lexicon
const KIT_FLAG = 'alfheim_starting_kit_v2'  // bumped for B-46: existing players need the petal safety net too

PlayerEvents.loggedIn(event => {
    const player = event.player
    const data = player.persistentData

    if (data.getBoolean(KIT_FLAG)) return
    data.putBoolean(KIT_FLAG, true)

    // Entries are either 'id' or ['id', count]. Stacks are built here rather than at script
    // load so the item registry is certainly populated.
    let granted = 0
    STARTING_KIT.forEach(entry => {
        const id = Array.isArray(entry) ? entry[0] : entry
        const count = Array.isArray(entry) ? entry[1] : 1
        const stack = Item.of(id, count)
        if (stack.isEmpty()) {
            console.warn(`[Alfheim Reclaimed] starting kit: unknown item '${id}' — skipped`)
            return
        }
        player.give(stack)
        granted++
    })

    console.info(`[Alfheim Reclaimed] starting kit issued to ${player.username} (${granted} item(s))`)
})

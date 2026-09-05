// Alfheim Reclaimed — Era III: the tier ladder begins
//
// Steps = 2n-3, so Era III is a 3-step chain and the first era with custom intermediates.
// Each step uses a different station, per CAMPAIGN_ERAS.md §1b rule 2 — a new process, not
// just a new item.
//
//   1. Petal Apothecary  petals + dreamwood        -> alfheim:living_fibre
//   2. Mana Pool         living_fibre  + 2000 mana -> alfheim:charged_fibre
//   3. Runic Altar       charged_fibre + runes     -> alfheim:verdant_filament
//
// Items come from tools/items_manifest.json via tools/gen_items.py.

ServerEvents.recipes(event => {
    const id = s => `alfheim:era3/${s}`

    // --------------------------------------------------- 1. Petal Apothecary
    // Green for growth, lime for what is coming back, and Dreamwood because the fibre is drawn
    // from it. Cheap on purpose — this is the step the player repeats most.
    event.custom({
        type: 'botania:petal_apothecary',
        ingredients: [
            { tag: 'botania:petals/green' },
            { tag: 'botania:petals/green' },
            { tag: 'botania:petals/lime' },
            { item: 'botania:dreamwood' }
        ],
        output: { item: 'alfheim:living_fibre', count: 2 },
        reagent: { tag: 'botania:seed_apothecary_reagent' }
    }).id(id('living_fibre'))

    // --------------------------------------------------- 2. Mana Pool infusion
    // No catalyst: this is meant to be reachable with the plain pool from Era II.
    event.custom({
        type: 'botania:mana_infusion',
        input: { item: 'alfheim:living_fibre' },
        mana: 2000,
        output: { item: 'alfheim:charged_fibre' }
    }).id(id('charged_fibre'))

    // --------------------------------------------------- 3. Runic Altar
    // Two runes, so the player must have run the altar twice before reaching this.
    event.custom({
        type: 'botania:runic_altar',
        ingredients: [
            { item: 'alfheim:charged_fibre' },
            { item: 'alfheim:charged_fibre' },
            { item: 'botania:rune_earth' },
            { item: 'botania:rune_water' },
            { tag: 'botania:mana_dusts' }
        ],
        mana: 5200,
        output: { item: 'alfheim:verdant_filament' }
    }).id(id('verdant_filament'))

    // --------------------------------------------------- Elven Quartz, native route
    // GATE_REVERSAL.md §2.2.D — Elven Quartz exists only as a gate trade output in stock
    // Botania. On the elven side it has to have a native origin, and Era III is where the
    // design places it.
    event.custom({
        type: 'botania:mana_infusion',
        input: { item: 'minecraft:quartz' },
        mana: 1500,
        output: { item: 'botania:quartz_elven' }
    }).id(id('elven_quartz_native'))

    console.info('[Alfheim Reclaimed] Era III tier ladder loaded.')
})

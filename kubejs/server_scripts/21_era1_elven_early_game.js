// Alfheim Reclaimed — Era I: the elven early game
//
// The reversal makes Livingwood a gate-import, and Botania's entire early game is built on it.
// Left alone, the player reaches the first flower and stops forever. This re-points that whole
// chain onto Dreamwood, which the Pure Daisy now produces natively.
//
// Nothing here removes a route before its replacement exists in the same file.
// See alfheim_reclaimed_design/GATE_REVERSAL.md §2.

ServerEvents.recipes(event => {
    const id = s => `alfheim:era1/${s}`

    // ---------------------------------------------------------------- Pure Daisy
    // As shipped: #minecraft:logs -> botania:livingwood_log, via Botania's state-copying
    // variant (it preserves log axis). Alfheim's daisies make Dreamwood instead.
    event.remove({ id: 'botania:pure_daisy/livingwood' })

    event.custom({
        type: 'botania:state_copying_pure_daisy',
        input: { type: 'tag', tag: 'minecraft:logs' },
        output: 'botania:dreamwood_log'
    }).id(id('pure_daisy_dreamwood'))

    // Livingrock is untouched — stone still converts, and the Diluted Pool needs it.

    // ---------------------------------------------------------------- Wand of the Forest
    // Shipped recipe calls for botania:livingwood_twig, which is now unobtainable.
    // Dreamwood Twig already has its own vanilla-shaped recipe from dreamwood logs.
    event.remove({ id: 'botania:twig_wand' })

    event.custom({
        type: 'botania:twig_wand',
        category: 'equipment',
        group: 'botania:twig_wand',
        key: {
            P: { tag: 'botania:petals' },
            S: { item: 'botania:dreamwood_twig' }
        },
        pattern: [' PS', ' SP', 'S  '],
        result: { item: 'botania:twig_wand' },
        show_notification: true
    }).id(id('twig_wand_dreamwood'))

    // ---------------------------------------------------------------- First spreader
    // The base Mana Spreader is livingwood + copper. Re-point the wood only; copper stays,
    // so this remains the cheap tier-one spreader.
    //
    // botania:elven_spreader is deliberately NOT touched — it needs Elementium, which is
    // Era V (mythicbotany:elementium_ore). It stays the upgrade it is meant to be.
    event.remove({ id: 'botania:mana_spreader' })

    event.shaped('botania:mana_spreader', [
        'WWW',
        'CP ',
        'WWW'
    ], {
        W: '#botania:dreamwood_logs',
        C: 'minecraft:copper_ingot',
        P: '#botania:petals'
    }).id(id('mana_spreader_dreamwood'))

    // ---------------------------------------------------------------- Recipe repair
    // MythicBotany ships feysythia_petal_apothecary as a forge:conditional gated on Feywild
    // being loaded. Feywild IS loaded, so the recipe activates — and then fails, because it
    // asks for feywild:lesser_fey_gem and Feywild 5.5.5 ships only feywild:fey_gem.
    // Result: mythicbotany:feysythia is uncraftable. Re-add with the item that exists.
    event.custom({
        type: 'botania:petal_apothecary',
        ingredients: [
            { tag: 'botania:petals/yellow' },
            { tag: 'botania:petals/yellow' },
            { tag: 'botania:petals/purple' },
            { item: 'feywild:fey_gem' }
        ],
        output: { item: 'mythicbotany:feysythia' },
        reagent: { tag: 'botania:seed_apothecary_reagent' }
    }).id(id('feysythia_repair'))

    console.info('[Alfheim Reclaimed] Era I elven early game loaded.')
})

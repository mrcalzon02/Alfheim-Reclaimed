// Alfheim Reclaimed — Era II: the spine interlock
//
// TWIN_SPINES.md §2.1 — Leaf feeds Song. Ars Nouveau's first Source generator is re-pointed
// onto Botania's Livingrock, so a player cannot bootstrap the Song tradition before they have
// working mana infrastructure. It is the mechanical claim that the two spines are one broken
// tradition rather than two alternatives.
//
// Era II is the right place for it: Livingrock is Era II's opening quest, and the Agronomic
// Sourcelink is Era II's Song midpoint. The dependency runs forward, never backward.

ServerEvents.recipes(event => {
    const id = s => `alfheim:era2/${s}`

    // ------------------------------------------------- Agronomic Sourcelink needs Livingrock
    // Shipped: source gems + gold ingots + wheat. Gold is swapped for Livingrock — the gem
    // and the wheat stay, so it still reads as an Ars Nouveau recipe rather than a Botania one.
    event.remove({ id: 'ars_nouveau:agronomic_sourcelink' })

    event.shaped('ars_nouveau:agronomic_sourcelink', [
        'GWG',
        'RSR',
        'RRR'
    ], {
        G: '#forge:gems/source',
        W: 'minecraft:wheat',
        R: 'botania:livingrock',
        S: 'ars_nouveau:source_gem_block'
    }).id(id('agronomic_sourcelink_livingrock'))

    console.info('[Alfheim Reclaimed] Era II spine interlock loaded.')
})

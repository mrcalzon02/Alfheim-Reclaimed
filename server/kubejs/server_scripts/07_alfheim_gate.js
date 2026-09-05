// Alfheim Reclaimed — the gate becomes buildable in Era IV
//
// Hand-written. Implements the recipe half of B-36; the traversal and the
// `alfheim_midgard_unlocked` flag stay with that item.
//
// ---------------------------------------------------------------------------------------------
// WHY THIS EXISTS. Found by tools/check_coverage.py's method-ordering check, 2026-09-04.
//
// `botania:elven_trade` recipes appear in Eras IV, VI, VII, VIII, IX and X. Their station is the
// Alfheim Portal. Botania crafts that portal from:
//
//     livingwood logs  +  terrasteel nuggets
//
// Both are unavailable here, and not by accident:
//
//   * Livingwood is a GATE-IMPORT in this pack (INSTRUCTIONS.md §1). The entire Era I chain was
//     re-pointed onto Dreamwood precisely because livingwood cannot be got.
//   * Terrasteel is the Era X capstone.
//
// So the station for six eras of recipes required a material from the last era and a material the
// premise says you cannot have. Every elven trade in the pack was unreachable, silently — the
// recipes load fine, there is simply no way to build the block that performs them.
//
// This re-lays the portal on Era IV's own capstone, which is what B-36 already specified:
// "the final component must come from the Era IV tier chain — alfheim:gatewrought_cord, whose
// tooltip has read 'Era IV. Elven work, finished on the far side of the gate' since the roster
// was authored."
//
// Removal and replacement ship together, per §6.1. One reachable route, per §6.2.
// ---------------------------------------------------------------------------------------------

ServerEvents.recipes(event => {
    const id = s => `alfheim:gate/${s}`

    // Out: livingwood + terrasteel, neither of which exists on this side of the gate.
    event.remove({ id: 'botania:alfheim_portal' })

    // In: dreamwood, which grows here, framing the Era IV capstone. The shape is Botania's own
    // 3x3 — a frame of wood around a vertical spine — so the recipe still reads as a portal
    // rather than as an arbitrary substitution.
    event.shaped('botania:alfheim_portal', [
        'WCW',
        'WCW',
        'WCW'
    ], {
        W: 'botania:dreamwood',
        C: 'alfheim:gatewrought_cord'
    }).id(id('alfheim_portal'))

    console.info('[Alfheim Reclaimed] Alfheim Portal re-gated onto Era IV (gatewrought_cord).')
})

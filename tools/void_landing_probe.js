// Development-only survey: where, if anywhere, can a terminal landing exist?
//
// check_void_surface_support reserves continentalness -0.94..-0.925 for `last_watch` and
// `starless_orrery`, at 1,800 solid blocks and minimum dimensions 14x8x14. The 2026-09-09
// verification found Starless Reach occupying 143 columns of a 384-block generated patch
// against the Verge's 76,146 -- no area to land on at any density. That is a property of the
// continentalness FIELD, not of the debris threshold, so no density edit can answer it and
// generating more chunks around an arbitrary site cannot either.
//
// This asks the field directly. A landing needs the band to persist across 14 blocks, which
// happens only where the continentalness gradient is shallow. The scan is coarse first, then
// refines around each hit, and reports the sites whose neighbourhood stays in band -- which
// the harness then force-generates so the terrain there can be measured for real.
var VoidContext = Java.loadClass('net.minecraft.world.level.levelgen.DensityFunction$SinglePointContext')

// The strip check_void_surface_support reserves.
var BAND_LO = -0.940
var BAND_HI = -0.925
// A landing is 14x14. Sample a 15x15 neighbourhood at 3-block steps: 25 probes per candidate.
var FOOT = 15
var STEP = 3
var COARSE = 64
var RADIUS = 12288

ServerEvents.loaded(event => {
  var server = event.server
  server.scheduleInTicks(40, callback => {
    var level = server.getLevel('mythicbotany:alfheim')
    var state = level.getChunkSource().randomState()
    var router = state.router()
    var continents = router.continents()

    function cont(x, z) { return Number(continents.compute(new VoidContext(x, 64, z))) }
    function inBand(c) { return c >= BAND_LO && c <= BAND_HI }

    // How much of a 15x15 neighbourhood stays inside the reserved band?
    function persistence(x, z) {
      var hit = 0, n = 0
      for (var dx = -FOOT / 2; dx <= FOOT / 2; dx += STEP) {
        for (var dz = -FOOT / 2; dz <= FOOT / 2; dz += STEP) {
          n++
          if (inBand(cont(x + dx, z + dz))) hit++
        }
      }
      return hit / n
    }

    var candidates = []
    var scanned = 0, inband = 0
    for (var x = -RADIUS; x <= RADIUS; x += COARSE) {
      for (var z = -RADIUS; z <= RADIUS; z += COARSE) {
        scanned++
        var c = cont(x, z)
        if (!inBand(c)) continue
        inband++
        var p = persistence(x, z)
        if (p >= 0.72) candidates.push({ x: x, z: z, cont: c, persistence: p })
      }
    }

    candidates.sort((a, b) => b.persistence - a.persistence)
    var best = candidates.slice(0, 6)

    console.log('[VOID LANDING] scanned ' + scanned + ' lattice points over +/-' + RADIUS
      + ', ' + inband + ' inside continentalness ' + BAND_LO + '..' + BAND_HI
      + ', ' + candidates.length + ' with a 15x15 neighbourhood at least 72% in band')
    for (var i = 0; i < best.length; i++) {
      console.log('[VOID LANDING]   candidate ' + (i + 1) + ': x=' + best[i].x + ' z=' + best[i].z
        + ' cont=' + best[i].cont.toFixed(4)
        + ' persistence=' + (best[i].persistence * 100).toFixed(0) + '%')
    }

    // Same marker the harness already watches, so it force-generates these and nothing else
    // needs to change. `kind` keeps the report readable next to the ordinary void audit.
    var sites = []
    for (var j = 0; j < best.length; j++) {
      sites.push({ x: best[j].x, z: best[j].z, kind: 'landing_candidate',
                   continentalness: best[j].cont, persistence: best[j].persistence })
    }
    console.log('[VOID AUDIT] SITES ' + JSON.stringify(sites))

    JsonIO.write('kubejs/void_terrain_result.json', {
      survey: 'terminal_landing',
      band: [BAND_LO, BAND_HI],
      radius: RADIUS,
      coarse_step: COARSE,
      lattice_points: scanned,
      in_band: inband,
      candidates: candidates.length,
      best: sites
    })
    console.log('[VOID AUDIT] COMPLETE errors=0')
  })
})

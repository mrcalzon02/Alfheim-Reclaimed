// Leyline network effects. This registry slice intentionally defines identity and presentation only.
// Runtime bonuses are added only after their Mine and Slash / Ars Nouveau hooks are proven.
StartupEvents.registry('mob_effect', event => {
  event.create('alfheim:leyline_presence')
    .displayName('Leyline Presence')
    .beneficial()
    .color(0x69e6ff)

  event.create('alfheim:ember_current')
    .displayName('Ember Current')
    .beneficial()
    .color(0xf06a2a)

  event.create('alfheim:tidal_recovery')
    .displayName('Tidal Recovery')
    .beneficial()
    .color(0x3d9cff)

  event.create('alfheim:rootguard')
    .displayName('Rootguard')
    .beneficial()
    .color(0x62a95a)

  event.create('alfheim:gale_tempo')
    .displayName('Gale Tempo')
    .beneficial()
    .color(0xa8f1df)

  event.create('alfheim:dusk_precision')
    .displayName('Dusk Precision')
    .beneficial()
    .color(0x8d5ed8)

  event.create('alfheim:dawn_clarity')
    .displayName('Dawn Clarity')
    .beneficial()
    .color(0xffd76a)
})

# Royal Tile Set I — Wave B room completion

**Status:** static source/generated validated; client rendering and field acceptance pending.

Wave B implements all 19 room-completion semantics from `tools/royal_tileset_catalog.json` as 28 physical custom-model blocks. The wave covers oath and offering furniture, crescent seating, banquet/salon tables, display and wardrobe storage, washstand/vanity furniture, candelabrum and pennant lighting/textile rhythm, tea service, scroll and lectern scholarship, carved panels, planters/trellises, and guard displays.

Large furniture uses local modules where repeated span materially matters: crescent settee, banquet table, salon table, glass display case, wardrobe, vanity and trough planter. Every block is directional, carries explicit structure rotation/mirror behavior, has bounded collision, and remains decorative rather than silently acquiring inventory or progression behavior.

Source is `tools/gen_royal_tileset_wave_b.py`; static verification is `tools/check_royal_tileset_wave_b.py`. The disposable gallery is placed with `/function alfheim:royal_tileset_wave_b/review`.

Evidence: generator reports 32 byte-identical outputs; checker reports `PASS semantics=19 blocks=28 generated=32`. Runtime acceptance remains pending.

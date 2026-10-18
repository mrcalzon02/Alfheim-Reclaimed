"""Pack-owned standalone works yield to valid Fairy Island grid reservations.

The commanded Greatbole and disabled ley fracture keep their existing behavior.
Layouts, biome restrictions, salts and terrain projection are preserved.
"""
FAMILIES=set('''anchor_bastion ashwatch_keep bloomfall_shrine boneyard_wreck
boughwatch_tower broken_causeway canopy_span capfall_barrow cinderglass_crater
driftwood_span drowned_arcade fen_shrine fracture_gate frostwatch_spire
garden_archive_terrace garland_menhirs golden_field_dais grange_hall grey_barrow
harvest_crater hillcrown_keep hillcut_quarry hollow_bastion hushbark_causeway
kings_cliff_tomb lake_arcade lake_shrine last_watch marchfall_crater mire_hulk
mistfall_shrine mourning_court plains_moot prism_observatory pyre_hall riven_hold
root_shrine rotwood_barrow silver_moot split_gallery sporebank_hall starless_orrery
starveling_pit stormwreck sundered_quarry tidal_arcade tidewatch_boughs warren_gate
waystone_ring'''.split())
TYPE='alfheim_companion:fairy_reserved_jigsaw'


def apply(path,value):
    path=str(path).replace('\\','/')
    name=path.rsplit('/',1)[-1].removesuffix('.json')
    if name not in FAMILIES or 'worldgen/structure/' not in path:return value
    if value.get('type') not in ('minecraft:jigsaw',TYPE):return value
    layout={k:v for k,v in value.items() if k not in ('type','layout')}
    return {**value,'type':TYPE,'layout':layout}

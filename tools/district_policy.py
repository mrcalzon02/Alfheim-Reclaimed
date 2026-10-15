"""Shared source policy for all twelve district authoring generators.

Identical candidate grid + native single-family winner = no cross-family starts.
Three prototype families retain definitions but receive no new natural sets.
"""
FAMILIES=('common_residential_quarter','elder_lineage_precinct','civic_center','relief_district',
          'scholastic_quarter','production_district','agricultural_estate','roads_trade',
          'harbor_complex','sacred_precinct','military_warden','frontier_stewardship')
PLACEMENT={'type':'minecraft:random_spread','spacing':192,'separation':96,'salt':202610150}


def apply(path,value):
    path=str(path).replace('\\','/')
    stem=path.rsplit('/',1)[-1].removesuffix('.json')
    if stem not in FAMILIES:return value
    if 'worldgen/structure_set/' in path:
        value={**value,'placement':dict(PLACEMENT)}
    elif 'worldgen/structure/' in path and value.get('type') in ('minecraft:jigsaw','alfheim_companion:remote_district'):
        layout={k:v for k,v in value.items() if k not in ('type','layout')}
        value={**value,'type':'alfheim_companion:remote_district','layout':layout}
    return value

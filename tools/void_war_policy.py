"""Non-destructive reservation wrapper for the six existing frontier neighbors."""
from copy import deepcopy
from pathlib import Path
FAMILIES={'edgewatch_beacon','strandline_hulk','severed_span','verge_spire','shore_memorial_court','thorn_gate'}
TYPE='alfheim_companion:void_war_neighbor'
def apply(path,body):
    path=Path(path)
    if path.parent.name!='structure' or path.stem not in FAMILIES or 'type' not in body:return body
    result=deepcopy(body)
    if result.get('type')==TYPE:return result
    if result.get('type')=='alfheim_companion:void_surface':return body
    assert result['type']=='minecraft:jigsaw',path
    result['layout']={k:v for k,v in result.items() if k!='type'};result['type']=TYPE
    return result

"""Native reservation wrapper for pack-owned underground layouts only."""
from copy import deepcopy
from pathlib import Path

FAMILIES={'deep_quarry','elder_kings_tomb','faultwork','deepworks_headworks','leyline_corridors'}
TYPE='alfheim_companion:allocated_underground'

def apply(path,body):
    path=Path(path)
    if path.parent.name!='structure' or path.stem not in FAMILIES or 'type' not in body:return body
    result=deepcopy(body)
    if result.get('type')==TYPE:return result
    assert result['type']=='minecraft:jigsaw',path
    result['layout']={k:v for k,v in result.items() if k!='type'}
    result['type']=TYPE
    return result

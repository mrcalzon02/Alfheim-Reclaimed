"""Court stations and final occupancy reservations shared by generation and migration."""
import copy
import json
import nbt

ELF = 'richs_races_wood_elves:wood_elf'
# Origins relative to the assembly datum (the baked marker is at .5,+1,-5.5).
ORIGINS = {'amphitheatre': (-24,-3,-72), 'west_residence': (-72,-5,-72),
           'east_service': (24,-5,-72), 'north_council': (-24,-5,-120)}
# Local feet coordinates; routes run from the station toward an existing door or aisle.
STATIONS = [
    dict(name='Magister Velrous', piece='amphitheatre', pos=(29,4,30), yaw=0, role='Magister', route=(29,32)),
    dict(name='Captain Orenvel', piece='amphitheatre', pos=(19,4,30), yaw=0, role='Guard Captain', route=(19,32)),
    dict(name='Sethyr the Quiet', piece='west_residence', pos=(34,6,35), yaw=180, role='Court Steward', route=(34,29)),
    dict(name='Loremistress Anwe', piece='north_council', pos=(12,6,35), yaw=-90, role='Archive', route=(19,35)),
    dict(name='Faelan Ashbound', piece='east_service', pos=(34,6,12), yaw=0, role='Provisioner', route=(34,18)),
    dict(name='Nyre of the Boughs', piece='north_council', pos=(36,6,35), yaw=90, role='Survey Records', route=(29,35)),
    dict(name='Warden Ilesh', piece='west_residence', pos=(41,6,26), yaw=-90, role='Court Watch', route=(43,24)),
    dict(name='Cinder-Sister Vaal', piece='east_service', pos=(12,6,12), yaw=0, role='Kitchen', route=(12,18)),
]

def reservation(station):
    x,y,z = station['pos']; tx,tz = station['route']
    cells = {(xx,yy,zz) for xx in range(x-1,x+2) for zz in range(z-1,z+2) for yy in range(y,y+3)}
    # Three-wide approach, ending at the existing room door or processional spine.
    while (x,z) != (tx,tz):
        x += (tx>x)-(tx<x) if x != tx else 0
        z += (tz>z)-(tz<z) if x == tx else 0
        for xx in range(x-1,x+2):
            for zz in range(z-1,z+2):
                for yy in range(y,y+3): cells.add((xx,yy,zz))
    return cells

def apply(pieces):
    old = {json.loads(e['nbt']['CustomName'])['text']: e
           for p in pieces.values() for e in p.entities if 'alfheim_hub_court' in e['nbt'].get('Tags',[])}
    assert set(old) == {s['name'] for s in STATIONS}
    for p in pieces.values():
        p.entities = [e for e in p.entities if 'alfheim_hub_court' not in e['nbt'].get('Tags',[])]
    for s in STATIONS:
        p = pieces['court/'+s['piece']]; x,y,z = s['pos']
        for xx,yy,zz in reservation(s):
            p.set(xx,yy,zz,('minecraft:air',None))
            # These are occupied interiors, at the existing shared floor elevation.
            p.set(xx,y-1,zz,('feywild:elven_quartz_block',None))
        e = copy.deepcopy(old[s['name']])
        e['pos'] = [nbt.Double(x+.5),nbt.Double(y),nbt.Double(z+.5)]
        e['blockPos'] = [nbt.Int(x),nbt.Int(y),nbt.Int(z)]
        e['nbt']['Rotation'] = [nbt.Float(s['yaw']),nbt.Float(0)]
        e['nbt']['Tags'] = ['alfheim_hub_court','alfheim_court_station_v2']
        p.entities.append(e)
    return pieces

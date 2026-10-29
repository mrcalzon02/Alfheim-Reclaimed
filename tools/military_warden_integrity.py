"""Military/Warden: complete authored footings and four rotated socket layouts.

This is a source-template check, not evidence of live terrain-fit or natural starts.
"""
from collections import deque

DIRECTIONS = {'north': (0, -1), 'east': (1, 0), 'south': (0, 1), 'west': (-1, 0)}
VOID = {'minecraft:air', 'minecraft:cave_air', 'minecraft:water',
        'minecraft:lava', 'minecraft:structure_void'}


def rotate(x, z, turns):
    for _ in range(turns):
        x, z = -z, x
    return x, z


def at(pos, origin, turns):
    x, y, z = map(int, pos)
    x, z = rotate(x, z, turns)
    return origin[0] + x, origin[1] + y, origin[2] + z


def cells(piece):
    return {tuple(map(int, b['pos'])): piece['palette'][int(b['state'])]['Name']
            for b in piece['blocks']}


def check_footing(piece, depth=8):
    """Absent cells are NOT solid: templates leave the existing world untouched."""
    sx, sy, sz = map(int, piece['size'])
    assert sy > depth and max(sx, sy, sz) <= 48, ('size', piece['size'])
    blocks = cells(piece)
    for x in range(sx):
        for z in range(sz):
            for y in range(depth):
                state = blocks.get((x, y, z))
                assert state is not None and state not in VOID, ('footing gap', x, y, z, state)
    return sx * sz * depth


def ports(piece):
    result = []
    for b in piece['blocks']:
        be = b.get('nbt', {})
        if be.get('id') == 'minecraft:jigsaw':
            state = piece['palette'][int(b['state'])]
            facing = state.get('Properties', {}).get('orientation', '').split('_')[0]
            assert facing in DIRECTIONS, ('port facing', b)
            result.append((tuple(map(int, b['pos'])), facing, be))
    return result


def bounding_box(piece, origin, turns):
    sx, sy, sz = map(int, piece['size'])
    points = [at((x, y, z), origin, turns)
              for x in (0, sx-1) for y in (0, sy-1) for z in (0, sz-1)]
    return tuple(min(p[i] for p in points) for i in range(3)) + tuple(max(p[i] for p in points) for i in range(3))


def check_rotations(pieces, links, anchor, depth=8):
    """Reconstruct the *actual* named jigsaw connections at every global rotation."""
    expected = set(links) | {child for children in links.values() for child in children.values()}
    assert set(pieces) == expected and anchor in pieces, ('family members', set(pieces), expected)
    footings = sum(check_footing(p, depth) for p in pieces.values())
    for root_rotation in range(4):
        pending = deque([(anchor, (0, 0, 0), root_rotation)])
        placed = {}
        joins = 0
        while pending:
            name, origin, turns = pending.popleft()
            assert name not in placed, ('duplicate piece', name)
            piece = pieces[name]
            box = bounding_box(piece, origin, turns)
            for other, old in placed.items():
                assert not all(max(box[i], old[i]) <= min(box[i+3], old[i+3])
                               for i in range(3)), ('overlap', root_rotation, name, other)
            placed[name] = box
            for face, child in links.get(name, {}).items():
                parent = [(pos, facing, be) for pos, facing, be in ports(piece)
                          if facing == face and be.get('pool', '').endswith('/'+child)]
                assert len(parent) == 1, ('outgoing socket', name, child)
                pos, facing, be = parent[0]
                incoming = [(p, f) for p, f, e in ports(pieces[child])
                            if e.get('name') == be['target'] and e.get('pool') == 'minecraft:empty']
                assert len(incoming) == 1, ('incoming socket', name, child)
                child_pos, child_face = incoming[0]
                dx, dz = rotate(*DIRECTIONS[facing], turns)
                child_turns = next((r for r in range(4)
                                    if rotate(*DIRECTIONS[child_face], r) == (-dx, -dz)), None)
                assert child_turns is not None, ('opposite face', name, child)
                start = at(pos, origin, turns)
                target = (start[0]+dx, start[1], start[2]+dz)
                relative = at(child_pos, (0, 0, 0), child_turns)
                child_origin = tuple(target[i]-relative[i] for i in range(3))
                assert at(child_pos, child_origin, child_turns) == target
                for member, point, data in ((name, pos, piece), (child, child_pos, pieces[child])):
                    x, y, z = point
                    blocks = cells(data)
                    assert y == depth+1, ('socket elevation', member, point)
                    assert blocks.get((x, y+1, z)) == 'minecraft:air', ('blocked headroom', member, point)
                    assert blocks.get((x, y-1, z)) not in (None, *VOID), ('unsupported socket', member, point)
                pending.append((child, child_origin, child_turns))
                joins += 1
        assert set(placed) == set(pieces) and joins == len(pieces)-1, ('incomplete layout', root_rotation)
    return {'rotations': 4, 'members': len(pieces), 'joins_per_rotation': len(pieces)-1,
            'foundation_cells': footings}


def self_test():
    def fixture(outgoing):
        palette = [{'Name': 'minecraft:stone'}, {'Name': 'minecraft:air'},
                   {'Name': 'minecraft:jigsaw', 'Properties': {
                       'orientation': 'north_up' if outgoing else 'south_up'}}]
        blocks = [{'pos': [x,y,z], 'state': 0 if y < 3 else 1}
                  for x in range(5) for y in range(7) for z in range(5)]
        socket = [2,3,0 if outgoing else 4]
        blocks = [b for b in blocks if b['pos'] != socket]
        blocks.append({'pos': socket, 'state': 2, 'nbt': {
            'id': 'minecraft:jigsaw', 'name': 'alfheim:child_in', 'target': 'alfheim:child_in',
            'pool': 'alfheim:ancient/military_warden/child' if outgoing else 'minecraft:empty'}})
        return {'size': [5,7,5], 'palette': palette, 'blocks': blocks}
    root, child = fixture(True), fixture(False)
    links = {'root': {'north': 'child'}}
    assert check_rotations({'root': root, 'child': child}, links, 'root', 2) == {
        'rotations': 4, 'members': 2, 'joins_per_rotation': 1, 'foundation_cells': 100}
    broken = fixture(False)
    broken['blocks'] = [b for b in broken['blocks'] if b['pos'] != [2,1,2]]
    try:
        check_footing(broken, 2)
        raise AssertionError('accepted missing foundation')
    except AssertionError as exc:
        assert exc.args[0][0] == 'footing gap'
    broken = fixture(False)
    next(b for b in broken['blocks'] if b['pos'] == [2,4,4])['state'] = 0
    try:
        check_rotations({'root': root, 'child': broken}, links, 'root', 2)
        raise AssertionError('accepted blocked doorway')
    except AssertionError as exc:
        assert exc.args[0][0] == 'blocked headroom'
    print('MILITARY/WARDEN INTEGRITY SELF-TEST PASS: 4 rotations; two negative controls')


if __name__ == '__main__':
    self_test()

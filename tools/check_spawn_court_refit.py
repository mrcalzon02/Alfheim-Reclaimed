"""Validate final occupied volumes and preserve quest identity across the refit."""
import json
from pathlib import Path
import nbt
from hub_court_layout import STATIONS, reservation

ROOT=Path(__file__).resolve().parents[1]

def main():
    names=[]
    for s in STATIONS:
        root=nbt.load(ROOT/f'kubejs/data/alfheim/structures/court/{s["piece"]}.nbt')[1]
        blocks={tuple(b['pos']):root['palette'][b['state']]['Name'] for b in root['blocks']}
        for pos in reservation(s):assert blocks.get(pos)=='minecraft:air',(s['name'],pos)
        x,y,z=s['pos'];assert blocks[x,y-1,z]=='feywild:elven_quartz_block'
        found=[e for e in root['entities'] if json.loads(e['nbt']['CustomName'])['text']==s['name']]
        assert len(found)==1 and list(found[0]['pos'])==[x+.5,y,z+.5]
        names.append(s['name'])
    links=json.loads((ROOT/'kubejs/data/quest_giver/quest_line_links.json').read_text())
    assert all(l['name'] in names and 'interaction_item' not in l for l in links)
    assert {l['quest_line_id'] for l in links}=={'the_reclaiming','the_royal_guard'}
    script=(ROOT/'kubejs/server_scripts/04_spawn_hub.js').read_text(encoding='utf-8')
    assert 'ENTITY_INTERACT_MODE, $PrivacyMode.PUBLIC' in script
    assert 'BLOCK_EDIT_MODE, $PrivacyMode.PRIVATE' in script
    migration=(ROOT/'kubejs/data/alfheim/functions/hub/court_refit/apply.mcfunction').read_text()
    assert 'kill ' not in migration and 'summon ' not in migration
    assert 'if score #court_count alfheim.hub matches 1' in migration
    assert 'if score #court_ready alfheim.hub matches 8 run tag @s' in migration
    for line in migration.splitlines():
        if 'run setblock' in line:assert line.startswith('execute if block ')
    print('COURT REFIT PASS: 8 unique NPCs; clear standing volumes and approaches; supported floors; stable quest links; guarded migration without NPC replacement.')

if __name__=='__main__':main()

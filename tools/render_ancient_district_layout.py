"""Draw a reviewable footprint map from the saved-assembly census."""
import json
import argparse
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import nbt
from check_ancient_assembly import rotate

ROOT=Path(__file__).resolve().parents[1]


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--family',choices=('common_residential','elder_lineage','civic_center','relief_district','scholastic_quarter','production_district','agricultural_estate','roads_trade','harbor_complex','sacred_precinct','military_warden','frontier_stewardship'),default='common_residential');args=ap.parse_args()
    lineage=args.family=='elder_lineage'
    civic=args.family=='civic_center'
    relief=args.family=='relief_district'
    scholastic=args.family=='scholastic_quarter'
    production=args.family=='production_district'
    agricultural=args.family=='agricultural_estate'
    trade=args.family=='roads_trade'
    harbor=args.family=='harbor_complex'
    frontier=args.family=='frontier_stewardship'
    military=args.family=='military_warden'
    sacred=args.family=='sacred_precinct'
    data=json.loads((ROOT/'tools'/('frontier_stewardship_runtime_census.json' if frontier else 'military_warden_runtime_census.json' if military else 'sacred_precinct_runtime_census.json' if sacred else 'harbor_complex_runtime_census.json' if harbor else 'roads_trade_runtime_census.json' if trade else 'agricultural_estate_runtime_census.json' if agricultural else 'production_district_runtime_census.json' if production else 'scholastic_quarter_runtime_census.json' if scholastic else 'relief_district_runtime_census.json' if relief else 'civic_center_runtime_census.json' if civic else 'elder_lineage_runtime_census.json' if lineage else 'ancient_district_runtime_census.json')).read_text())
    colors={'neighborhood_common_hall':('#d6b566','Common hall'),
            'common_row_house':('#a3bea5','Row house'),'courtyard_home':('#6da796','Garden home'),
            'artisan_house_shop':('#b78f68','Workshop'),'extended_kin_hall':('#aa98ba','Kin hall'),
            'district_cistern':('#83b5c2','Cistern'),'district_mass_grave':('#b18a8a','Burial edge'),
            'collapsed_trace_field':('#c9c4b6','Trace')}
    if lineage:
        colors={'palace_center':('#d6b566','Audience hall'),'ancestral_gallery':('#baa7c0','Ancestral gallery'),
                'family_residence':('#b7a783','Family residence'),'ancestor_court':('#80b6a4','Ancestor garden'),
                'family_mausoleum':('#a5a0b8','Family mausoleum'),'gate_court':('#cec4a9','Entrance court'),
                'retainer_house':('#a5b49a','Retainer house'),'household_service':('#bd996f','Service wing'),
                'processional_entry':('#c3bcac','Processional gate')}
    if civic:
        colors={'assembly_hall':('#d6b566','Assembly hall'),'record_house':('#baa7c0','Record house'),
                'council_house':('#b7a783','Council house'),'public_forum':('#80b6a4','Public forum'),
                'market_court':('#a5b49a','Market court'),'service_court':('#cec4a9','Service court'),
                'census_hall':('#a5a0b8','Census hall'),'public_kitchen':('#bd996f','Public kitchen'),
                'processional_avenue':('#c3bcac','Processional avenue')}
    if relief:
        colors={'triage_court':('#d6b566','Triage court'),'hospice_hall':('#baa7c0','Hospice hall'),
                'healer_cloister':('#b7a783','Healer cloister'),'quarantine_checkpoint':('#a5b49a','Quarantine checkpoint'),
                'mass_grave':('#b18a8a','Last Order graves'),'supply_court':('#cec4a9','Supply court'),
                'ration_hall':('#a5a0b8','Ration hall'),'sealed_store':('#bd996f','Sealed store'),
                'corpse_cart_way':('#c3bcac','Cart approach'),'ash_pits':('#939185','Ash pits'),
                'digger_shelter':('#80b6a4','Digger shelter')}
    if scholastic:
        colors={'lore_college':('#d6b566','Lore college'),'archive_cloister':('#baa7c0','Archive cloister'),
                'runic_engineering_hall':('#b7a783','Runic engineering'),'philosopher_court':('#80b6a4','Philosopher court'),
                'astral_conservatory':('#a5a0b8','Astral conservatory'),'entry_court':('#cec4a9','Entry court'),
                'student_residence':('#a5b49a','Student residence'),'botanical_research_garden':('#bd996f','Research garden'),
                'scholars_avenue':('#c3bcac','Scholars avenue')}
    if production:
        colors={'freight_yard':('#d6b566','Freight yard'),'distribution_depot':('#baa7c0','Distribution depot'),
                'resonance_foundry':('#b7a783','Resonance foundry'),'mana_mill':('#80b6a4','Mana mill'),
                'dreamwood_shaping_court':('#a5a0b8','Dreamwood shaping'),'glass_bloom_house':('#93b5bb','Glass Bloom house'),
                'waterworks':('#83b5c2','Dry waterworks'),'worker_housing':('#a5b49a','Worker housing'),
                'guard_post':('#bd996f','Guard post'),'freight_approach':('#c3bcac','Freight approach')}
    if agricultural:
        colors={'water_garden':('#83b5c2','Water garden'),'terraced_orchard':('#80b6a4','Terraced orchard'),
                'survival_terraces':('#b7a783','Survival terraces'),'root_granary':('#d6b566','Root granary'),
                'seed_vault':('#baa7c0','Seed vault'),'fungus_conservatory':('#a5a0b8','Fungus conservatory'),
                'harvest_court':('#cec4a9','Harvest court'),'keeper_housing':('#a5b49a','Keeper housing'),
                'pollinator_sanctuary':('#bd996f','Pollinator sanctuary'),'farm_approach':('#c3bcac','Farm approach')}
    if trade:
        colors={'caravan_court':('#d6b566','Caravan court'),'processional_avenue':('#80b6a4','Processional avenue'),
                'bridge_gate':('#93b5bb','Bridge gate'),'freight_exchange':('#baa7c0','Freight exchange'),
                'custom_house':('#b7a783','Custom house'),'bonded_store':('#a5a0b8','Bonded store'),
                'road_checkpoint':('#cec4a9','Road checkpoint'),'wayshrine_rest':('#a5b49a','Wayshrine / rest'),
                'refugee_lodge':('#bd996f','Refugee lodge'),'road_approach':('#c3bcac','Road approach')}
    if harbor:
        colors={'harbor_exchange':('#d6b566','Harbor exchange'),'harbormaster_house':('#80b6a4','Harbormaster house'),
                'bonded_warehouse':('#b7a783','Bonded warehouse'),'wavebreak_pier':('#93b5bb','Wavebreak pier'),
                'sunken_drydock':('#83b5c2','Sunken drydock'),'tide_temple':('#baa7c0','Tide temple'),
                'quay_court':('#cec4a9','Quay court'),'signal_lighthouse':('#a5b49a','Signal lighthouse'),
                'dockworker_housing':('#bd996f','Dockworker housing'),'harbor_approach':('#c3bcac','Harbor approach')}
    if sacred:
        colors={'great_temple_court':('#d6b566','Great Temple Court'),'root_star_shrine':('#80b6a4','Root and Star shrine'),
                'ancestor_reflection_pool':('#83b5c2','Ancestor reflection pool'),'pilgrim_chapel':('#a5b49a','Pilgrim chapel'),
                'rite_house':('#b7a783','Rite House'),'temple_reliquary':('#baa7c0','Temple reliquary'),
                'processional_approach':('#c3bcac','Processional approach')}
    if military:
        colors={'border_keep':('#d6b566','Border Keep'),'warden_tower':('#a5b49a','Warden Tower'),
                'watch_captain_house':('#b7a783','Captain House'),'gate_barracks':('#baa7c0','Gate Barracks'),
                'discipline_guard_court':('#cec4a9','Guard Court'),'last_muster_ground':('#b18a8a','Last Muster Ground')}
    if frontier:
        colors={'green_noble_lodge':('#d6b566','Hunting Lodge'),'surveyor_tower':('#a5b49a','Surveyor Tower'),
                'forest_waystation':('#b7a783','Forest Waystation'),'outlying_retreat_hall':('#baa7c0','Retreat Hall'),
                'moon_pool_sanctuary':('#83b5c2','Moon Pool'),'wild_ward_shrine':('#80b6a4','Wild Ward Shrine')}
    rects=[]
    for node in data['layout']:
        _,p=nbt.load(str(ROOT/f'kubejs/data/alfheim/structures/ancient/{args.family}/{node["name"]}.nbt'))
        sx,_,sz=map(int,p['size']);x,_,z=node['origin'];r=node['rotation']
        corners=[rotate(a,b,r) for a,b in ((0,0),(sx-1,0),(sx-1,sz-1),(0,sz-1))]
        rect=(min(a for a,b in corners)+x,min(b for a,b in corners)+z,
              max(a for a,b in corners)+x+1,max(b for a,b in corners)+z+1)
        rects.append((node['name'],rect))
    x0=min(r[0] for _,r in rects);z0=min(r[1] for _,r in rects)
    x1=max(r[2] for _,r in rects);z1=max(r[3] for _,r in rects)
    scale=5;pad=70;top=120
    im=Image.new('RGB',(int((x1-x0)*scale+pad*2),int((z1-z0)*scale+top+140)), '#f0eee7')
    draw=ImageDraw.Draw(im)
    font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',14)
    title=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',29)
    sub=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',19)
    draw.text((pad,25),'Frontier / Wilderness Stewardship' if frontier else 'Military / Warden Precinct' if military else 'Sacred Precinct' if sacred else 'Harbor Complex Prototype' if harbor else 'Roads / Trade Precinct' if trade else 'Agricultural Estate / Food Belt' if agricultural else 'Production District' if production else 'Scholastic Quarter' if scholastic else 'Relief / Quarantine District' if relief else 'Civic Center' if civic else 'Elder Lineage Precinct' if lineage else 'Common Residential Quarter',fill='#273630',font=title)
    subtitle='Saved assembly • 9 members • 8 supported joins • 152 cultural modules' if lineage else 'Saved assembly • 26 pieces • 16 inhabited members • 25 supported joins'
    if civic:subtitle='Saved assembly • 9 members • 8 supported joins • 101 cultural modules'
    if relief:subtitle='Saved assembly • 11 members • 10 supported joins • 56 cultural modules'
    if scholastic:subtitle='Saved assembly • 9 members • 8 supported joins • 89 cultural modules'
    if production:subtitle='Saved assembly • 10 members • 9 supported joins • 32 cultural modules'
    if agricultural:subtitle='Saved assembly • 10 members • 9 supported joins • 41 cultural modules'
    if trade:subtitle='Saved assembly • 10 members • 9 supported joins • 47 cultural modules'
    if harbor:subtitle='Saved assembly • 10 members • 9 supported joins • 72 cultural modules'
    if sacred:subtitle='Saved assembly - 7 members - 6 supported joins - 59 cultural modules'
    if military:subtitle='Saved assembly - 6 members - 5 supported joins'
    if frontier:subtitle='Saved assembly - 6 members - 5 supported joins'
    draw.text((pad,68),subtitle,fill='#425249',font=sub)
    for name,r in rects:
        box=(pad+(r[0]-x0)*scale,top+(r[1]-z0)*scale,pad+(r[2]-x0)*scale,top+(r[3]-z0)*scale)
        color,label=colors.get(name,('#d2d0c7','Avenue'))
        draw.rectangle(box,fill=color,outline='#526056',width=2)
        cx=(box[0]+box[2])/2;cz=(box[1]+box[3])/2
        lines=[];line=''
        for word in label.split():
            trial=(line+' '+word).strip()
            if line and draw.textlength(trial,font=font)>box[2]-box[0]-12:
                lines.append(line);line=word
            else:line=trial
        lines.append(line)
        draw.multiline_text((cx,cz),'\n'.join(lines),fill='#22352b',font=font,anchor='mm',align='center')
    y=im.height-92
    draw.text((pad,y),'Top-down template footprints; north is up. Scale: one block = five pixels.',fill='#425249',font=sub)
    draw.text((pad,y+34),f'Extent: {x1-x0} × {z1-z0} blocks. Terrain and visual acceptance remain pending.',fill='#425249',font=sub)
    out=ROOT/'alfheim_reclaimed_design'/('frontier_stewardship_layout.png' if frontier else 'military_warden_layout.png' if military else 'sacred_precinct_layout.png' if sacred else 'harbor_complex_layout.png' if harbor else 'roads_trade_layout.png' if trade else 'agricultural_estate_layout.png' if agricultural else 'production_district_layout.png' if production else 'scholastic_quarter_layout.png' if scholastic else 'relief_district_layout.png' if relief else 'civic_center_layout.png' if civic else 'elder_lineage_precinct_layout.png' if lineage else 'common_residential_quarter_layout.png')
    im.save(out)
    print(out)


if __name__=='__main__':main()

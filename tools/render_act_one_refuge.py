"""Readable shop floor plans from emitted NBT, with the actual service stock."""
from PIL import Image,ImageDraw,ImageFont
import nbt
from gen_act_one_refuge import ROOT,RES,REPORT,SERVICES,NAMES


def main():
    font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',17)
    title=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',25)
    small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',14)
    canvas=Image.new('RGB',(1440,1020),'#17212a');d=ImageDraw.Draw(canvas)
    d.text((24,15),'ASHEN CLOISTER / ACT I COMBAT SERVICE REFUGE',font=title,fill='white')
    d.text((24,53),'Actual emitted shop floor plans. Six native merchants; 43 offers. Offline plan, not a game screenshot.',font=font,fill='#b4c4ca')
    summaries=[['Native MMO equipment','Sword, bow and staff','Three armor families','Shield','Common, level one','4 Manasteel + 4 Source Gems'],
        ['Travel and combat provisions','Beef, bread and milk','Arrows and torches','MMO life, mana, energy food','Food 1-2 Manasteel','and 1-2 Source Gems'],
        ['Healing and resource potions','Common, uncommon, rare','Regeneration and speed','Fire and water protection','Night vision','1-6 Manasteel + 1-6 Gems'],
        ['Paid repairs preserve item data','1 Manasteel + 1 Source Gem','per 100 missing durability','Crouch and interact with gear','Anvil, grindstone, XP bottles','Sharpening stones'],
        ['Combat additives','Six MMO buff potions','Strength, dexterity, intellect','Might, arcane and critical','Sharpening stones','Native weapon/armor enchants'],
        ['Profession salvage barter','16 common MMO materials','plus 1 Source Gem','for 2 common health potions','Mining, farming, meat, fishing','Four exchanges; bounded stock']]
    colors={'minecraft:air':'#c1c5b0','minecraft:spruce_planks':'#876c4e','minecraft:mossy_stone_bricks':'#52684e','minecraft:barrel':'#bf904b','minecraft:flower_pot':'#9a6150'}
    for i,service in enumerate(SERVICES):
        x=18+(i//2)*474;y=100+(i%2)*435
        d.rounded_rectangle((x,y,x+458,y+415),10,fill='#22323d')
        d.text((x+12,y+12),NAMES[i],font=font,fill='white')
        root=nbt.load(RES/f'data/alfheim/structures/ashen_refuge/{service}.nbt')[1]
        cells={tuple(b['pos']):root['palette'][b['state']]['Name'] for b in root['blocks']}
        for xx in range(13):
            for z in range(19):
                name=cells[(xx,5,z)];color=colors.get(name,'#91b6c1')
                a,b=x+15+xx*14,y+52+z*14
                d.rectangle((a,b,a+12,b+12),fill=color)
        a,b=x+15+6*14,y+52+9*14;d.ellipse((a,b,a+12,b+12),fill='#effcf1',outline='#000000',width=2)
        for line,text in enumerate(summaries[i]):d.text((x+213,y+70+line*30),text,font=small,fill='#d2dce1')
        d.text((x+15,y+343),'White marker: merchant. Brown: counter. Blue: workbench.',font=small,fill='#a9bfca')
        d.text((x+15,y+370),'13 x 19 plot; three-wide street-facing entrance.',font=small,fill='#a9bfca')
    d.text((24,985),'Stock resets once per 24,000 game ticks. Native MMO restrictions apply. Natural placement and client review remain pending.',font=small,fill='#b4c4ca')
    canvas.save(REPORT/'town_services.png')
    print('Rendered six shop floor plans from generated structure NBT.')


if __name__=='__main__':main()

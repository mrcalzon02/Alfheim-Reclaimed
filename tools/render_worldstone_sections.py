"""Plot actual saved chunk blocks; this is a measurement diagram, not a screenshot."""
import argparse,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from run_worldstone_validation import load_world,ROOT


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--report',default='tools/worldstone_runtime_report.json');args=ap.parse_args()
    report=json.loads((ROOT/args.report).read_text());grid,required,block=load_world(report)
    image=Image.new('RGB',(1320,960),'#f2f0ed');draw=ImageDraw.Draw(image)
    def font(size,bold=False):
        return ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf' if bold else 'C:/Windows/Fonts/segoeui.ttf',size)
    draw.text((34,23),'THE MOUNTAIN WORLDSTONE',font=font(29,True),fill='#231e29')
    draw.text((34,68),'Measured from saved Minecraft chunks · flat material colours · not a client screenshot',font=font(17),fill='#615d68')
    colors={'alfheim_companion:worldstone_crystal':'#9c0d24','alfheim_companion:worldstone_heart':'#ff3346',
            'alfheim_companion:worldstone_fragment_ore':'#743343','alfheim_companion:worldstone_cluster':'#f35b61',
            'alfheim:obsidian_livingrock':'#34323d','alfheim:cracked_livingrock':'#514d59',
            'alfheim:starfleck_livingrock':'#655d76','minecraft:bedrock':'#191820','minecraft:water':'#285b7b',
            'minecraft:lava':'#b85e32','minecraft:grass_block':'#60734b','minecraft:snow':'#dee2ec'}
    def color(name,sky=False):
        if name in ('minecraft:air','minecraft:cave_air',None):return '#d7e3e9' if sky else '#151621'
        if name in colors:return colors[name]
        if 'leaves' in name:return '#56684b'
        if 'dirt' in name:return '#6e594e'
        return '#8e8690'
    panel=Image.new('RGB',(237,385));pixels=panel.load()
    for xx,x in enumerate(range(-118,119)):
        surface=next((y for y in range(320,-65,-1) if block(x,y,0) not in (None,'minecraft:air','minecraft:cave_air')), -64)
        for y in range(-64,321):pixels[xx,320-y]=ImageColor(color(block(x,y,0),y>surface))
    panel=panel.resize((474,770),Image.Resampling.NEAREST);image.paste(panel,(72,132))
    draw.rectangle((71,131,546,902),outline='#9a949b')
    for y in (-64,0,64,128,192,256,320):
        py=132+(320-y)*2;draw.line((62,py,70,py),fill='#615d68');draw.text((17,py-11),str(y),font=font(15),fill='#615d68')
    draw.text((72,105),'Vertical cut through the mountain and chamber',font=font(16,True),fill='#3c3541')
    draw.text((72,916),'Horizontal span: 237 blocks · vertical scale: 2 pixels per block',font=font(14),fill='#615d68')
    plan=Image.new('RGB',(237,237));pix=plan.load()
    for xx,x in enumerate(range(-118,119)):
        for zz,z in enumerate(range(-118,119)):pix[xx,zz]=ImageColor(color(block(x,60,z)))
    plan=plan.resize((474,474),Image.Resampling.NEAREST);image.paste(plan,(626,132))
    draw.rectangle((625,131,1100,606),outline='#9a949b');draw.text((626,105),'Horizontal cut at Y60',font=font(16,True),fill='#3c3541')
    site=report['site']
    lines=[f"Mountain summit: Y{site['summit']}",f"Minimum sampled rock cover: {site['minimum_sampled_cover']} blocks",
           'Main crystal: approximately 136 blocks tall','Cavern: roughly 230 blocks wide and 200 high',
           'Open air below and above the suspended crystal']
    for i,text in enumerate(lines):draw.text((626,638+i*31),text,font=font(18,i==0),fill='#342c39')
    legend=[('#ff3346','Radiant crystal heart'),('#9c0d24','Budding crimson crystal'),
            ('#743343','Fragment ore'),('#34323d','Cavern stone'),('#151621','Open cavern air')]
    for i,(c,label) in enumerate(legend):
        col=i%2;row=i//2;px=626+col*278;py=810+row*31
        draw.rectangle((px,py+3,px+18,py+21),fill=c);draw.text((px+28,py),label,font=font(16),fill='#504754')
    draw.text((626,920),f"Alfheim · X {site['x']} · Z {site['z']}",font=font(15),fill='#615d68')
    path=ROOT/'tools/worldstone_art/saved_world_sections.png';image.save(path);print(path)


def ImageColor(value):
    return tuple(bytes.fromhex(value.lstrip('#')))


if __name__=='__main__':main()

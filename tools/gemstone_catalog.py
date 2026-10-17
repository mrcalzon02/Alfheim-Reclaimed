"""Natural gem roster and explicit game distribution; not a claim of exhaustive mineralogy.

Names distinguish mineral varieties, ornamental rocks and organic/biogenic materials.
Deposit pools and Y bands are authored gameplay abstractions, not geological measurements.
"""
SOURCES=[
 'https://www.gia.edu/gem-encyclopedia',
 'https://www.gia.edu/gia-gem-project-various-gems-a',
 'https://www.gia.edu/gia-gem-project-various-gems-b-c',
 'https://cibjo.org/wp-content/uploads/2023/01/22-12-22-Official-Gemstone-Book.pdf',
 'https://www.gia.edu/amber','https://www.gia.edu/pearl',
 'https://4cs.gia.edu/en-us/blog/captivated-coral/']
GEMS=[];POOLS={}
REUSE={'diamond':'minecraft:diamond','emerald':'minecraft:emerald','amethyst':'minecraft:amethyst_shard','rock_crystal':'minecraft:quartz','lapis_lazuli':'minecraft:lapis_lazuli'}

def add(pool,label,y,rarity,color,habit,entries,kind='mineral',source='stone'):
    POOLS[pool]={'id':pool,'label':label,'y':list(y),'rarity':rarity,'color':color,'habit':habit,'kind':kind,'source':source,'gems':[]}
    for text in entries.split('|'):
        # key : display name : optional hex : optional weight
        fields=text.strip().split(':');key=fields[0];name=fields[1] if len(fields)>1 and fields[1] else key.replace('_',' ').title()
        row={'id':key,'name':name,'pool':pool,'kind':kind,'color':fields[2] if len(fields)>2 and fields[2] else color,'weight':int(fields[3]) if len(fields)>3 else 4,'habit':habit,'item':REUSE.get(key,'alfheim:gem_'+key)}
        GEMS.append(row);POOLS[pool]['gems'].append(key)

add('carbon','Carbon crystal seam',(-60,-8),32,'b7ebf5','faceted',
    'diamond:Diamond::12|yellow_diamond:Yellow Diamond:f0d85f:2|pink_diamond:Pink Diamond:e99dbb:1|blue_diamond:Blue Diamond:7295d4:1|black_diamond:Black Diamond:343b47:2')
add('corundum','Corundum pocket',(-48,48),16,'bb365e','faceted',
    'ruby:Ruby:d93b67:8|star_ruby:Star Ruby:bd5270:1|sapphire:Sapphire:4965db:10|pink_sapphire:Pink Sapphire:ef94b9:4|yellow_sapphire:Yellow Sapphire:edcf56:4|green_sapphire:Green Sapphire:71a97b:3|purple_sapphire:Purple Sapphire:a375cd:3|white_sapphire:White Sapphire:d5e9ee:4|padparadscha:Padparadscha Sapphire:f49879:1|star_sapphire:Star Sapphire:678dbf:1')
add('beryl','Beryl-bearing rock',(-32,96),16,'62c5ae','faceted',
    'emerald:Emerald:45bf7a:6|aquamarine:Aquamarine:76d7e8:10|morganite:Morganite:edb4c9:6|heliodor:Heliodor:e5d56d:6|goshenite:Goshenite:d9eef0:8|red_beryl:Red Beryl:d85b77:1')
add('quartz','Quartz crystal pocket',(-40,160),7,'be8dd7','crystal',
    'rock_crystal:Rock Crystal:e0eaf0:12|amethyst:Amethyst:a67cdf:10|citrine:Citrine:e5bb5e:7|ametrine:Ametrine:ba81d5:3|rose_quartz:Rose Quartz:eeb2cd:7|smoky_quartz:Smoky Quartz:9c897f:8|morion:Morion:47434d:3|rutilated_quartz:Rutilated Quartz:dcbd7e:3|tourmalinated_quartz:Tourmalinated Quartz:b6c1c4:3|prasiolite:Prasiolite:a8cfac:1')
add('chalcedony','Chalcedony nodule',(-8,128),8,'c98a6c','banded',
    'agate:Agate:c58b74|moss_agate:Moss Agate:709a78|dendritic_agate:Dendritic Agate:b6b894|fire_agate:Fire Agate:d6974e:2|blue_lace_agate:Blue Lace Agate:a6c8ee|carnelian:Carnelian:e37745|sard:Sard:945239|onyx:Onyx:353c46|sardonyx:Sardonyx:b16a50|chrysoprase:Chrysoprase:75ce9b|chrome_chalcedony:Chrome Chalcedony:489c74:2|bloodstone:Bloodstone:43694d|red_jasper:Red Jasper:b65347|yellow_jasper:Yellow Jasper:d1a857|picture_jasper:Picture Jasper:b8a17c|ocean_jasper:Ocean Jasper:88ab96|dalmatian_stone:Dalmatian Stone:c9ba99|aventurine:Aventurine:70ac85|tiger_eye:Tiger Eye:b88d49|hawk_eye:Hawk Eye:598391')
add('opal','Opal-bearing nodule',(16,144),15,'a9d8df','opal',
    'white_opal:White Opal:cadfe8:10|black_opal:Black Opal:4d5c7e:2|fire_opal:Fire Opal:f39b55:5|boulder_opal:Boulder Opal:8c8b9a:4|common_opal:Common Opal:b3cfbe:10|water_opal:Water Opal:9fcbd8:3|hyalite:Hyalite:d2e9c2:2')
add('garnet','Garnet-bearing seam',(-56,64),12,'ae4059','faceted',
    'almandine:Almandine Garnet:a24559:10|pyrope:Pyrope Garnet:c23d53:9|spessartine:Spessartine Garnet:e79849:6|grossular:Grossular Garnet:b5ca73:6|hessonite:Hessonite Garnet:c28445:4|tsavorite:Tsavorite Garnet:4db879:2|andradite:Andradite Garnet:b0a55c:5|demantoid:Demantoid Garnet:7cb55c:1|topazolite:Topazolite Garnet:d0b54d:2|uvarovite:Uvarovite Garnet:3a9b6c:2|rhodolite:Rhodolite Garnet:b45880:5|malaya_garnet:Malaya Garnet:d7978b:2|color_change_garnet:Color-change Garnet:937aa9:1')
add('tourmaline','Tourmaline pegmatite',(-16,128),17,'8bbd9c','crystal',
    'elbaite:Elbaite:8ecb96:7|rubellite:Rubellite:d56c9f:5|indicolite:Indicolite:4f9fb7:4|verdelite:Verdelite:54aa77:6|schorl:Schorl:333b48:10|dravite:Dravite:ad946c:6|watermelon_tourmaline:Watermelon Tourmaline:d98cad:3|bicolor_tourmaline:Bicolor Tourmaline:98b5d2:3|paraiba_tourmaline:Paraiba-type Tourmaline:5ad4cf:1|liddicoatite:Liddicoatite:ac84b1:2')
add('feldspar','Gem feldspar lens',(32,224),9,'a6c5d7','cabochon',
    'moonstone:Moonstone:c8d6eb:8|rainbow_moonstone:Rainbow Moonstone:b4d8e8:5|labradorite:Labradorite:6ca5bb:9|spectrolite:Spectrolite:637caa:2|sunstone:Sunstone:e5a568:7|amazonite:Amazonite:7dccbb:8|andesine:Andesine:d9a38d:3|orthoclase:Orthoclase:e2d193:5|sanidine:Sanidine:ccbbae:3')
add('olivine','Olivine crystal seam',(-48,64),18,'b0cc59','faceted','peridot:Peridot:b4d25f:12')
add('topaz','Topaz-bearing vein',(-32,160),22,'d9b578','faceted',
    'colorless_topaz:Colorless Topaz:d9e9e7:9|golden_topaz:Golden Topaz:e1ba67:8|imperial_topaz:Imperial Topaz:e39a66:2|pink_topaz:Pink Topaz:e6a6bd:2|pale_blue_topaz:Pale Blue Topaz:afd6df:2')
add('spinel','Spinel-bearing marble',(-48,80),24,'d46d8a','faceted',
    'red_spinel:Red Spinel:d7617c:8|blue_spinel:Blue Spinel:6d83c9:5|pink_spinel:Pink Spinel:e99fbd:7|black_spinel:Black Spinel:343746:9|color_change_spinel:Color-change Spinel:9f82b6:1')
add('chrysoberyl','Chrysoberyl pocket',(-48,48),40,'bbbe69','cabochon',
    'chrysoberyl:Chrysoberyl:c7cc73:10|alexandrite:Alexandrite:7da8a1:1|chrysoberyl_catseye:Chrysoberyl Cat\'s-eye:bab47d:2')
add('spodumene','Spodumene pegmatite',(-16,112),25,'c7a1cd','crystal',
    'kunzite:Kunzite:dfb3d9:8|hiddenite:Hiddenite:a9c986:3|triphane:Triphane:e0d9a2:7')
add('zoisite','Zoisite lens',(0,112),28,'8198c5','faceted',
    'tanzanite:Tanzanite:8c86d6:3|thulite:Thulite:d18f9c:8|ruby_in_zoisite:Ruby in Zoisite:719b77:7')
add('jade','Jade-bearing rock',(16,160),24,'74b18e','cabochon',
    'jadeite:Jadeite:80c69e:5|nephrite:Nephrite:6d9b7c:10|maw_sit_sit:Maw-sit-sit:5baf7a:2')
add('ornamental','Ornamental mineral pocket',(8,192),16,'62b4ad','cabochon',
    'turquoise:Turquoise:5bc4bd|variscite:Variscite:93c5a0|lapis_lazuli:Lapis Lazuli:4668bc|sodalite:Sodalite:6a80b9|hackmanite:Hackmanite:a48ab7:2|sugilite:Sugilite:ae75bc:2|charoite:Charoite:a48dc3:3|larimar:Larimar:99d5df:2|lazulite:Lazulite:5878ba|dumortierite:Dumortierite:667bb6')
add('metamorphic','Mixed silicate pocket',(-32,176),20,'8aa5a0','crystal',
    'andalusite:Andalusite:b59b7d|chiastolite:Chiastolite:b0a28a|kyanite:Kyanite:749dc9|iolite:Iolite:7a79b8|staurolite:Staurolite:a58b6c|scapolite:Scapolite:dfcb88|diopside:Diopside:93b98c|chrome_diopside:Chrome Diopside:4ea979|violane:Violane:9991bf|enstatite:Enstatite:b2a57d|bronzite:Bronzite:b69b6a|hypersthene:Hypersthene:8d8191|actinolite:Actinolite:789c80|clinohumite:Clinohumite:d9aa6d|axinite:Axinite:aa8a9a|epidote:Epidote:93a565|prehnite:Prehnite:b4d1a1|vesuvianite:Vesuvianite:adb77c|seraphinite:Seraphinite:7d9d8c|titanite:Titanite:c5bf75')
add('hydrothermal','Hydrothermal gem vein',(-48,96),19,'78bfc1','crystal',
    'apatite:Apatite:72c8ce|fluorite:Fluorite:ae94cf|calcite:Calcite:ead9ac|aragonite:Aragonite:e0c9a8|azurite:Azurite:4c75bc|malachite:Malachite:57a47b|chrysocolla:Chrysocolla:63bbb2|dioptase:Dioptase:46b395:2|smithsonite:Smithsonite:a3d2c1|rhodochrosite:Rhodochrosite:df9dad|rhodonite:Rhodonite:c78fa0|hemimorphite:Hemimorphite:9ad5df|cerussite:Cerussite:d6d9c2|anglesite:Anglesite:d5d5b1|barite:Barite:d7bba7|celestite:Celestite:a4c4e8|selenite:Selenite:e3e0d5|gypsum:Gypsum:d4c9ba|phosphophyllite:Phosphophyllite:a5d2c2:1')
add('metallic','Lustrous mineral seam',(-56,80),24,'c2a277','metallic',
    'pyrite:Pyrite:c3ad67|marcasite:Marcasite:adad8d|hematite:Hematite:727c8c|magnetite:Magnetite:464c56|cassiterite:Cassiterite:887465|cuprite:Cuprite:b96b66|rutile:Rutile:b68c70|sphalerite:Sphalerite:c49360|willemite:Willemite:b1c985:2|scheelite:Scheelite:d8ac72:2')
add('collector','Rare collector crystal pocket',(-24,224),64,'b4c6da','faceted',
    'zircon:Zircon:b5cbca:8|hyacinth_zircon:Hyacinth Zircon:d4a17e:5|green_zircon:Green Zircon:9ab38f:2|euclase:Euclase:a6d7df:3|phenakite:Phenakite:dce4dd:3|beryllonite:Beryllonite:e4e2c4:2|amblygonite:Amblygonite:d8dba3:4|montebrasite:Montebrasite:c9dba9:3|petalite:Petalite:e4ced7:5|lepidolite:Lepidolite:b19cc5:6|herderite:Herderite:c9d7a3:2|hambergite:Hambergite:e0dfc7:2|taaffeite:Taaffeite:bba0c3:1|musgravite:Musgravite:a398b1:1|benitoite:Benitoite:8397dc:1|jeremejevite:Jeremejevite:adcce6:1|grandidierite:Grandidierite:80bcb5:1|kornerupine:Kornerupine:a6b88d:2|serendibite:Serendibite:537b80:1|sinhalite:Sinhalite:c4ad76:2|painite:Painite:a76f64:1|poudretteite:Poudretteite:e4b8d1:1|pezzottaite:Pezzottaite:d68aaf:1|brazilianite:Brazilianite:c2d57c:2|apophyllite:Apophyllite:d0e5d9:5|danburite:Danburite:e4d7c7:4|diaspore:Diaspore:c7bd9c:3|sillimanite:Sillimanite:a8b7a7:3|scolecite:Scolecite:e4e3d9:4|natrolite:Natrolite:d9e0d5:4|analcime:Analcime:d6c9d0:4|leucite:Leucite:d7d9c9:4|pollucite:Pollucite:d9d8df:2|legrandite:Legrandite:ded18b:1')
add('highland','Highland gem pocket',(112,280),28,'a2c8dd','crystal',
    'phenomenal_quartz:Cat\'s-eye Quartz:ccc5a1:5|star_quartz:Star Quartz:d6b7c5:3|fluorapatite:Fluorapatite:a3c5c9:6|sphene_catseye:Cat\'s-eye Titanite:b7bd82:1')
add('amber','Fossil resin bed',(32,192),16,'d9a34d','amber',
    'amber:Amber:dfac54:10|inclusion_amber:Inclusion Amber:d39442:3|copal:Copal:e0bd6c:6',kind='organic',source='woodland_soil')
add('jet','Jet-bearing fossil wood',(-24,96),24,'3d4047','cabochon',
    'jet:Jet:373944:10|petrified_wood:Petrified Wood:bda07c:8|agatized_wood:Agatized Wood:ba8b6e:4',kind='fossil',source='woodland_fossil')
add('fossil','Gem-bearing fossil bed',(-32,128),32,'bbab97','fossil',
    'ammolite:Ammolite:82b6a5:2|agatized_coral:Agatized Coral:c5aa8f:5|fossil_ivory:Fossil Ivory:dfd3af:3|fossil_bone:Fossil Bone:c9bfa3:8',kind='fossil',source='stone')
add('pearl','Pearl oyster bed',(0,128),10,'e3d5d0','pearl',
    'white_pearl:White Pearl:e7e2dc:12|cream_pearl:Cream Pearl:e5d9b2:8|pink_pearl:Pink Pearl:e6bfc7:5|golden_pearl:Golden Pearl:dcc17e:3|black_pearl:Black Pearl:6b7187:2|conch_pearl:Conch Pearl:e3a5ae:1|melo_pearl:Melo Pearl:dfaa77:1|mother_of_pearl:Mother-of-pearl:b7d2d5:16',kind='biogenic',source='aquatic_shell')
add('coral','Precious coral growth',(0,128),16,'d57870','coral',
    'red_coral:Red Precious Coral:d46f62:9|pink_coral:Pink Precious Coral:e4a9a7:6|white_coral:White Precious Coral:dfd8ca:5|black_coral:Black Coral:524a46:3',kind='biogenic',source='aquatic_coral')

ALIASES={'iolite':['cordierite'],'titanite':['sphene'],'vesuvianite':['idocrase'],'larimar':['blue pectolite'],'morion':['black smoky quartz'],'phenomenal_quartz':["cat's-eye quartz"],'paraiba_tourmaline':['copper-bearing tourmaline'],'moonstone':['adularescent feldspar'],'maw_sit_sit':['jade-bearing ornamental rock'],'dalmatian_stone':['dalmatian jasper (trade name)']}
for g in GEMS:g['aliases']=ALIASES.get(g['id'],[])
# Shared pearl items can have a second biologically appropriate collection source.
POOLS['freshwater_pearl']={'id':'freshwater_pearl','label':'Freshwater mussel bed','y':[0,128],'rarity':10,'color':'d9d1c3','habit':'pearl','kind':'biogenic','source':'aquatic_shell','gems':['white_pearl','cream_pearl','pink_pearl','mother_of_pearl']}
assert len({g['id'] for g in GEMS})==len(GEMS)

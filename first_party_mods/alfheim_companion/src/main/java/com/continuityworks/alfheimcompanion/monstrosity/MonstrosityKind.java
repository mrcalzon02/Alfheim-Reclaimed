package com.continuityworks.alfheimcompanion.monstrosity;

public enum MonstrosityKind {
    TROLL("hulking_troll","Hulking Troll",1.5F,3.6F,90,12,.22,6,2.8,14,55,new String[]{"Mossback","Granite","Rime"}),
    CYCLOPS("cyclops","Cyclops",1.35F,3.2F,76,10,.23,4,3.0,16,50,new String[]{"Highland","Ashen","Sepulchral"}),
    BRIAR("briar_beast","Briar Beast",1.6F,1.9F,52,7,.31,5,2.0,9,32,new String[]{"Rootbound","Withered","Bloomthorn"}),
    INFESTOR("thorn_infestor","Thorn Infestor",1.1F,2.25F,42,5,.21,3,4.0,14,48,new String[]{"Thornlash","Sporethorn","Frostthorn"}),
    GARGOYLE("stone_gargoyle","Stone Gargoyle",1.0F,2.1F,60,8,.29,8,2.0,10,38,new String[]{"Basalt","Prism","Grave"}),
    HAG("fen_hag","Hag",.75F,2.35F,38,4,.27,1,6.5,20,65,new String[]{"Fen","Mire","Rime"}),
    WENDIGO("hollow_stag_wendigo","Wendigo",1.4F,3.8F,100,13,.28,4,3.2,18,60,new String[]{"Hollowwood","Barrowbone","Hoarfrost"}),
    DUSKWEAVER("duskweaver","Duskweaver",1.65F,1.55F,48,6,.32,3,2.2,10,38,new String[]{"Gloamsilk","Sporeveil","Starless"}),
    BRIDE("hollow_bride","Hollow Bride",.85F,2.8F,48,6,.25,2,3.5,18,55,new String[]{"Moonveil","Mourning","Rimeveil"}),
    MAW("barrow_maw","Barrow Maw",1.6F,2.1F,70,9,.24,7,2.4,14,48,new String[]{"Rootgrave","Mirebloom","Sepulchral"}),
    NUCKELAVEE("nuckelavee","Nuckelavee",1.3F,3.2F,86,11,.31,4,3,16,55,new String[]{"Brinebound","Cinderhide","Rimebound"}),
    REDCAP("redcap_reaver","Redcap Reaver",.8F,1.45F,32,6,.36,3,1.9,8,24,new String[]{"Thorncoat","Ashcoat","Frostcoat"}),
    CRYSTAL_COLOSSUS("corrupted_crystal_colossus","Corrupted Crystal Colossus",1.7F,3.45F,110,14,.21,10,3,20,64,new String[]{"Fractured","Blighted","Voidscarred"}),
    SHARD_REAVER("shard_reaver","Shard Reaver",1.15F,2.7F,64,9,.30,6,2.8,12,40,new String[]{"Amethyst","Viridian","Nullglass"}),
    PRISM_WARDEN("prism_warden","Prism Warden",1.25F,2.9F,78,7,.24,8,6,22,60,new String[]{"Riven","Venomed","Starless"}),
    MARROW_TICK("marrow_tick","Marrow Tick",.9F,.65F,18,3,.33,3,1.6,7,28,new String[]{"Pallid","Desiccated","Calcified"}),
    RIB_BURROWER("rib_burrower","Rib Burrower",1.35F,1.05F,32,5,.30,5,1.9,10,36,new String[]{"Fleshbound","Huskbound","Bonebound"}),
    SINEW_LEECH("sinew_leech","Sinew Leech",1.2F,.85F,26,4,.26,1,1.8,9,36,new String[]{"Coagulated","Withered","Mineralized"}),
    PARASITE_MAW("parasite_maw","Parasite Maw",1.8F,1.6F,64,8,.17,2,2.4,16,52,new String[]{"Bloated","Huskfed","Bonefed"});

    public final String id,label;public final float width,height;public final double health,damage,speed,armor,reach;
    public final int windup,cooldown;public final String[] variants;
    MonstrosityKind(String id,String label,float width,float height,double health,double damage,double speed,double armor,double reach,int windup,int cooldown,String[] variants){
        this.id=id;this.label=label;this.width=width;this.height=height;this.health=health;this.damage=damage;this.speed=speed;this.armor=armor;this.reach=reach;this.windup=windup;this.cooldown=cooldown;this.variants=variants;
    }
    public boolean spawnerOnly(){return this==MARROW_TICK||this==RIB_BURROWER||this==SINEW_LEECH||this==PARASITE_MAW;}
    public boolean crystal(){return this==CRYSTAL_COLOSSUS||this==SHARD_REAVER||this==PRISM_WARDEN;}
    public int variantFor(String biome){
        return switch(this){
            case TROLL->biome.contains("starved")?2:biome.contains("highland")||biome.contains("shatter")?1:0;
            case CYCLOPS->biome.contains("sepulchral")?2:biome.contains("ashen")||biome.contains("scorch")?1:0;
            case BRIAR->biome.contains("bloomfall")?2:biome.contains("hollow")||biome.contains("ashen")?1:0;
            case INFESTOR->biome.contains("starved")?2:biome.contains("mire")||biome.contains("fen")?1:0;
            case GARGOYLE->biome.contains("sepulchral")||biome.contains("starless")?2:biome.contains("prism")?1:0;
            case CRYSTAL_COLOSSUS,SHARD_REAVER,PRISM_WARDEN->biome.contains("shore")?2:biome.contains("prism")?1:0;
            case MARROW_TICK,RIB_BURROWER,SINEW_LEECH,PARASITE_MAW->0;
            case WENDIGO->biome.contains("starved")?2:biome.contains("sepulchral")?1:0;
            case DUSKWEAVER->biome.contains("starless")?2:biome.contains("sporebank")||biome.contains("fen")?1:0;
            case BRIDE->biome.contains("starved")?2:biome.contains("sepulchral")||biome.contains("mire")?1:0;
            case MAW->biome.contains("sepulchral")?2:biome.contains("mire")||biome.contains("sporebank")?1:0;
            case NUCKELAVEE->biome.contains("starved")?2:biome.contains("scorch")?1:0;
            case REDCAP->biome.contains("starved")?2:biome.contains("ashen")?1:0;
            case HAG->biome.contains("starved")?2:biome.contains("mire")||biome.contains("sporebank")?1:0;
        };
    }
}

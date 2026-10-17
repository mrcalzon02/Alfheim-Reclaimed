package com.continuityworks.alfheimcompanion.monstrosity;

public enum MonstrosityKind {
    TROLL("hulking_troll","Hulking Troll",1.5F,3.6F,90,12,.22,6,2.8,14,55,new String[]{"Mossback","Granite","Rime"}),
    CYCLOPS("cyclops","Cyclops",1.35F,3.2F,76,10,.23,4,3.0,16,50,new String[]{"Highland","Ashen","Sepulchral"}),
    BRIAR("briar_beast","Briar Beast",1.6F,1.9F,52,7,.31,5,2.0,9,32,new String[]{"Rootbound","Withered","Bloomthorn"}),
    INFESTOR("thorn_infestor","Thorn Infestor",1.1F,2.25F,42,5,.21,3,4.0,14,48,new String[]{"Thornlash","Sporethorn","Frostthorn"}),
    GARGOYLE("stone_gargoyle","Stone Gargoyle",1.0F,2.1F,60,8,.29,8,2.0,10,38,new String[]{"Basalt","Prism","Grave"}),
    HAG("fen_hag","Hag",.75F,2.35F,38,4,.27,1,6.5,20,65,new String[]{"Fen","Mire","Rime"});

    public final String id,label;public final float width,height;public final double health,damage,speed,armor,reach;
    public final int windup,cooldown;public final String[] variants;
    MonstrosityKind(String id,String label,float width,float height,double health,double damage,double speed,double armor,double reach,int windup,int cooldown,String[] variants){
        this.id=id;this.label=label;this.width=width;this.height=height;this.health=health;this.damage=damage;this.speed=speed;this.armor=armor;this.reach=reach;this.windup=windup;this.cooldown=cooldown;this.variants=variants;
    }
    public int variantFor(String biome){
        return switch(this){
            case TROLL->biome.contains("starved")?2:biome.contains("highland")||biome.contains("shatter")?1:0;
            case CYCLOPS->biome.contains("sepulchral")?2:biome.contains("ashen")||biome.contains("scorch")?1:0;
            case BRIAR->biome.contains("bloomfall")?2:biome.contains("hollow")||biome.contains("ashen")?1:0;
            case INFESTOR->biome.contains("starved")?2:biome.contains("mire")||biome.contains("fen")?1:0;
            case GARGOYLE->biome.contains("sepulchral")||biome.contains("starless")?2:biome.contains("prism")?1:0;
            case HAG->biome.contains("starved")?2:biome.contains("mire")||biome.contains("sporebank")?1:0;
        };
    }
}

package com.continuityworks.alfheimcompanion.client;

import com.continuityworks.alfheimcompanion.enemy.EnemyProfiles;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.geom.*;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.resources.ResourceLocation;

/** Habitat anatomy on native animation rigs: charcoal brute, frost exile and void stalker. */
public final class RegionalMonstrosityModels {
    public static final String[] SPECIES={"zombie","pillager","enderman"};
    public static ModelLayerLocation location(String species) {
        return new ModelLayerLocation(new ResourceLocation("alfheim_companion","regional/"+species),"main");
    }
    public static boolean matches(String species,int profile) {
        String biome=switch(species) {
            case "zombie"->"alfheim:ashen_grove";case "pillager"->"alfheim:starved_reach";
            case "enderman"->"alfheim:void_verge";default->"";
        };
        return !biome.isEmpty() && EnemyProfiles.get(profile).biome().equals(biome);
    }
    private static CubeListBuilder box(int u,int v,float x,float y,float z,float w,float h,float d) {
        return CubeListBuilder.create().texOffs(u,v).addBox(x,y,z,w,h,d);
    }
    public static LayerDefinition layer(String species) {
        boolean ash=species.equals("zombie"),rime=species.equals("pillager"),voidling=species.equals("enderman");
        if(!ash&&!rime&&!voidling)throw new IllegalArgumentException(species);
        var mesh=HumanoidModel.createMesh(CubeDeformation.NONE,0);var root=mesh.getRoot();
        var head=root.addOrReplaceChild("head",ash?box(0,0,-3.5F,-8,-4,7,8,6):
            rime?box(0,0,-3,-10,-3,6,10,6):box(0,0,-4,-8,-4,8,8,8),
            PartPose.offset(0,ash?1:voidling?-13:0,ash?-1:0));
        root.addOrReplaceChild("hat",CubeListBuilder.create(),PartPose.ZERO);
        head.addOrReplaceChild("hat",CubeListBuilder.create(),PartPose.ZERO);
        if(ash)head.addOrReplaceChild("jaw",box(32,0,-3.5F,-1,-4.5F,7,2,4),PartPose.ZERO);
        if(rime)head.addOrReplaceChild("nose",box(24,0,-1,-4,-5,2,4,2),PartPose.ZERO);
        if(voidling)head.addOrReplaceChild("chin",box(32,0,-2,0,-2,4,2,4),PartPose.ZERO);
        root.addOrReplaceChild("body",ash?box(0,24,-4.5F,0,-4,9,11,6):
            rime?box(0,24,-3.5F,0,-2.5F,7,12,5):box(0,24,-2.5F,0,-1.5F,5,11,3),
            PartPose.offset(0,voidling?-13:0,0));
        if(rime)root.addOrReplaceChild("arms",box(32,4,-5,-1,-2,10,3,4),PartPose.offset(0,3,-1));
        float legLength=voidling?25:12,armLength=voidling?28:ash?13:12;
        float width=voidling?1.5F:ash?4:3;
        for(int side:new int[]{-1,1}) {
            String name=side<0?"right":"left";
            var arm=root.addOrReplaceChild(name+"_arm",box(40,24,-width/2,-2,-width/2,width,armLength,width),
                PartPose.offset(side*(ash?6:rime?5:3.5F),voidling?-11:2,ash?-1:0));
            if(voidling)for(int digit=0;digit<2;digit++)arm.addOrReplaceChild("finger"+digit,
                box(48,48,-.7F+digit*.9F,armLength-2,-.6F,.5F,3,1.2F),PartPose.ZERO);
            root.addOrReplaceChild(name+"_leg",box(0,44,-(voidling?1:1.5F),0,-1.5F,voidling?2:3,legLength,3),
                PartPose.offset(side*(voidling?1.5F:2),voidling?-1:12,0));
        }
        return LayerDefinition.create(mesh,64,64);
    }
    private RegionalMonstrosityModels() {}
}

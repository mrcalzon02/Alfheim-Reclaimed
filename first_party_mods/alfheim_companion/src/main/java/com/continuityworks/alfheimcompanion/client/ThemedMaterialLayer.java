package com.continuityworks.alfheimcompanion.client;

import com.continuityworks.alfheimcompanion.enemy.EnemyAppearance;
import com.continuityworks.alfheimcompanion.enemy.EnemyProfiles;
import com.mojang.blaze3d.vertex.PoseStack;
import java.util.List;
import net.minecraft.client.model.*;
import net.minecraft.client.model.geom.*;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.client.renderer.*;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.monster.AbstractIllager;
import net.minecraftforge.client.event.EntityRenderersEvent;

/** Animated native geometry, not a flat colour swap. Three outfits per ecology:
 * bound cuirass/cuffs, shrouded hood/mantle, crowned asymmetric armour.
 * Eight material grammars add roots, fungal caps, crystal tines, mist collars,
 * ice fins, charred splinters, tidal fronds or harvest crests. Native textures
 * are sampled directly; vanilla and third-party texture files are untouched.
 */
public final class ThemedMaterialLayer<T extends Mob,M extends EntityModel<T>> extends RenderLayer<T,M> {
    private static final List<String> SPECIES=List.of("zombie","skeleton","pillager","enderman","endermite");
    private static final List<String> PARTS=List.of("head","body","right_arm","left_arm","right_leg","left_leg");
    private final ModelPart[][] outfits=new ModelPart[8][3];
    private final String species;
    private static ModelLayerLocation location(String species,int theme,int style) {
        return new ModelLayerLocation(new ResourceLocation("alfheim_companion","enemy/"+species+"_"+theme+"_"+style),"outfit");
    }
    public static void registerLayers(EntityRenderersEvent.RegisterLayerDefinitions event) {
        for(String species:SPECIES) for(int theme=0;theme<8;theme++) for(int style=0;style<3;style++) {
            final int t=theme,s=style;
            event.registerLayerDefinition(location(species,t,s),()->mesh(species,t,s));
        }
    }
    public ThemedMaterialLayer(RenderLayerParent<T,M> parent,EntityRendererProvider.Context context,String species) {
        super(parent);this.species=species;
        for(int theme=0;theme<8;theme++) for(int style=0;style<3;style++)
            outfits[theme][style]=context.bakeLayer(location(species,theme,style));
    }
    private static CubeListBuilder box(float x,float y,float z,float w,float h,float d) {
        return CubeListBuilder.create().texOffs(0,0).addBox(x,y,z,w,h,d,new CubeDeformation(0.16F));
    }
    private static void cube(PartDefinition part,String name,float x,float y,float z,float w,float h,float d) {
        part.addOrReplaceChild(name,box(x,y,z,w,h,d),PartPose.ZERO);
    }
    public static LayerDefinition mesh(String species,int theme,int style) {
        MeshDefinition mesh=new MeshDefinition();var root=mesh.getRoot();
        if(species.equals("endermite")) {
            // Separate animated segments retain the mite's curling locomotion.
            for(int i=0;i<4;i++) {
                var segment=root.addOrReplaceChild("segment"+i,CubeListBuilder.create(),PartPose.ZERO);
                float width=i==1 ? 5 : i==2 ? 3 : 4;
                cube(segment,"shell",-width/2,-0.6F,-1.6F,width,1.2F,3.2F);
                if(style==0) { cube(segment,"left",-width/2-1,-1,0,1,2,1);cube(segment,"right",width/2,-1,0,1,2,1); }
                if(style==1) cube(segment,"mantle",-width/2-0.4F,-1.2F,-2,width+0.8F,1.5F,4);
                if(style==2) cube(segment,"crest",-0.5F,-3.5F,-0.5F,1,4,1);
                var accent=segment.addOrReplaceChild("detail",CubeListBuilder.create(),PartPose.ZERO);
                ornament(accent,theme,style,true);
            }
        } else {
            for(String name:PARTS) root.addOrReplaceChild(name,CubeListBuilder.create(),PartPose.ZERO);
            var head=root.getChild("head");var body=root.getChild("body");
            boolean tall=species.equals("enderman"),thin=tall || species.equals("skeleton");
            float bodyDepth=species.equals("pillager") ? 3 : 2;
            float headTop=species.equals("pillager") ? -10 : -8;
            if(style==0) {
                cube(body,"cuirass",-4,1,-bodyDepth-0.25F,8,8,bodyDepth*2+0.5F);
                cube(head,"brow",-4.2F,headTop-0.2F,-4.2F,8.4F,1.4F,1);
            } else if(style==1) {
                cube(head,"hood_left",-4.35F,headTop,-4.2F,1, -headTop,8.4F);
                cube(head,"hood_right",3.35F,headTop,-4.2F,1,-headTop,8.4F);
                cube(head,"hood_top",-4.35F,headTop-1,-4.2F,8.7F,1,8.4F);
                cube(head,"hood_back",-3.35F,headTop,3.5F,6.7F,-headTop,1);
                cube(body,"mantle",-5,-0.5F,bodyDepth+0.35F,10,tall ? 20 : 17,0.8F);
                cube(body,"collar",-5,-0.5F,-bodyDepth-0.4F,10,2,bodyDepth*2+0.8F);
            } else {
                cube(body,"breastplate",-3.3F,1,-bodyDepth-0.35F,6.6F,8,1);
                cube(body,"belt",-4,10,-bodyDepth-0.2F,8,2,bodyDepth*2+0.4F);
                cube(head,"crown_band",-4.2F,headTop-0.2F,-4.2F,8.4F,1,8.4F);
            }
            for(String side:List.of("right_arm","left_arm","right_leg","left_leg")) {
                var part=root.getChild(side);boolean arm=side.endsWith("arm");
                float length=tall ? 30 : 12,width=thin ? 2 : 4;
                float x=arm ? (side.startsWith("right") ? -width+1 : -1) : -width/2;
                if(style==0) cube(part,"cuff",x,length-5,-width/2,width,3,width);
                if(style==1 && !arm) cube(part,"gaiter",x,length-6,-width/2,width,5,width);
                if(style==2 && side.equals("right_arm")) cube(part,"pauldron",x-0.4F,-1,-width/2-0.4F,width+0.8F,4,width+0.8F);
                var detail=part.addOrReplaceChild("detail",CubeListBuilder.create(),PartPose.ZERO);
                if(style==2 && side.equals("left_arm")) cube(detail,"brace",x,4,-width/2,width,2,width);
            }
            var decoration=head.addOrReplaceChild("detail",CubeListBuilder.create(),PartPose.offset(0,headTop,0));
            ornament(decoration,theme,style,false);
            var seal=body.addOrReplaceChild("detail",CubeListBuilder.create(),PartPose.ZERO);
            cube(seal,"seal",-1,style==1 ? 2 : 5,-bodyDepth-0.65F,2,2,0.7F);
        }
        return LayerDefinition.create(mesh,16,16);
    }
    private static void ornament(PartDefinition p,int theme,int style,boolean mite) {
        float k=mite ? 0.45F : 1;
        if(theme==1) { // fungal cap, shelf or split cap according to outfit
            cube(p,"cap",-4*k,-(style+2)*k,-3*k,8*k,1.5F*k,6*k);
            cube(p,"stem",-0.6F*k,-(style+2)*k,-0.6F*k,1.2F*k,(style+2)*k,1.2F*k);
            if(style==2) cube(p,"shelf",2*k,-1*k,0,4*k,1*k,3*k);
        } else if(theme==0 || theme==6 || theme==7) {
            int count=style==2 ? 3 : 2;
            for(int i=0;i<count;i++) cube(p,"frond"+i,(-3+i*2)*k,-(2+i%2+style)*k,1*k,1*k,(3+style)*k,1*k);
        } else if(theme==3) {
            cube(p,"veil",-3.7F*k,0,3.95F*k,7.4F*k,(4+style*2)*k,0.5F*k);
        } else {
            for(int i=0;i<(style==2 ? 3 : 1);i++)
                cube(p,"tine"+i,(-2+i*2)*k,-(3+style+i%2)*k,0,1.3F*k,(3+style+i%2)*k,1.3F*k);
        }
    }
    private ModelPart parentPart(String name) {
        if(getParentModel() instanceof HumanoidModel<?> model) return switch(name) {
            case "head"->model.head;case "body"->model.body;case "right_arm"->model.rightArm;
            case "left_arm"->model.leftArm;case "right_leg"->model.rightLeg;default->model.leftLeg;
        };
        if(getParentModel() instanceof HierarchicalModel<?> model) return model.root().getChild(name);
        throw new IllegalStateException("Unsupported themed enemy rig");
    }
    private void renderPart(PoseStack pose,MultiBufferSource buffers,int light,ModelPart part,
                            EnemyProfiles.Profile profile) {
        boolean details=part.hasChild("detail");ModelPart detail=details ? part.getChild("detail") : null;
        if(details) detail.visible=false;
        int rgb=profile.body();
        part.render(pose,buffers.getBuffer(RenderType.entityCutoutNoCull(profile.texture())),light,OverlayTexture.NO_OVERLAY,
            ((rgb>>16)&255)/255F,((rgb>>8)&255)/255F,(rgb&255)/255F,1);
        if(details) {
            detail.visible=true;rgb=profile.accent();
            detail.render(pose,buffers.getBuffer(RenderType.entityCutoutNoCull(profile.detailTexture())),light,OverlayTexture.NO_OVERLAY,
                ((rgb>>16)&255)/255F,((rgb>>8)&255)/255F,(rgb&255)/255F,1);
        }
    }
    @Override public void render(PoseStack pose,MultiBufferSource buffers,int light,T mob,float limbSwing,
            float limbAmount,float partialTick,float age,float yaw,float pitch) {
        if(mob.isInvisible()) return;
        var profile=EnemyProfiles.get(EnemyAppearance.profile(mob));
        var outfit=outfits[profile.theme()][EnemyAppearance.style(mob)];
        if(species.equals("endermite")) {
            for(int i=0;i<4;i++) {pose.pushPose();parentPart("segment"+i).translateAndRotate(pose);
                renderPart(pose,buffers,light,outfit.getChild("segment"+i),profile);pose.popPose();}
            return;
        }
        for(String name:PARTS) {
            EquipmentSlot slot=name.equals("head") ? EquipmentSlot.HEAD : name.endsWith("leg") ? EquipmentSlot.LEGS : EquipmentSlot.CHEST;
            if(!mob.getItemBySlot(slot).isEmpty()) continue; // armour remains the outermost surface
            // Crossed illager arms have their own vanilla geometry: don't attach to hidden arms.
            if(mob instanceof AbstractIllager illager && name.endsWith("arm")
                && illager.getArmPose()==AbstractIllager.IllagerArmPose.CROSSED) continue;
            pose.pushPose();
            if(getParentModel().young) {
                float scale=name.equals("head") ? 0.75F : 0.5F;
                pose.scale(scale,scale,scale);pose.translate(0,name.equals("head") ? 1 : 1.5,0);
            }
            parentPart(name).translateAndRotate(pose);
            renderPart(pose,buffers,light,outfit.getChild(name),profile);pose.popPose();
        }
    }
}

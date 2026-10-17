package com.continuityworks.alfheimcompanion.client;

import com.continuityworks.alfheimcompanion.gem.ModEternityCrown;
import com.google.gson.*;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.geom.*;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.client.extensions.common.IClientItemExtensions;
import java.io.*;
import java.nio.charset.StandardCharsets;

/** Worn geometry shares the generated item mesh, including all 232 individual insets. */
public final class EternityCrownAppearance implements IClientItemExtensions {
    private HumanoidModel<LivingEntity> model;
    @Override public HumanoidModel<?> getHumanoidArmorModel(LivingEntity entity,ItemStack stack,EquipmentSlot slot,HumanoidModel<?> original){
        if(model==null)model=create();
        int count=ModEternityCrown.progress(stack)*8;
        for(int i=0;i<232;i++)model.head.getChild("gem_"+i).visible=i<count;
        return model;
    }
    private static HumanoidModel<LivingEntity> create(){
        var mesh=new MeshDefinition();var root=mesh.getRoot();
        for(String part:new String[]{"head","hat","body","left_arm","right_arm","left_leg","right_leg"})root.addOrReplaceChild(part,CubeListBuilder.create(),PartPose.ZERO);
        var head=root.getChild("head");
        try(var input=EternityCrownAppearance.class.getResourceAsStream("/assets/alfheim_companion/crown_geometry.json")){
            var entries=JsonParser.parseReader(new InputStreamReader(input,StandardCharsets.UTF_8)).getAsJsonArray();
            int metal=0;
            for(var entry:entries){
                var e=entry.getAsJsonObject();var a=e.getAsJsonArray("from");var b=e.getAsJsonArray("to");var uv=e.getAsJsonArray("uv");
                float x=a.get(0).getAsFloat()-8,y=-6-b.get(1).getAsFloat(),z=a.get(2).getAsFloat()-8;
                float dx=b.get(0).getAsFloat()-a.get(0).getAsFloat(),dy=b.get(1).getAsFloat()-a.get(1).getAsFloat(),dz=b.get(2).getAsFloat()-a.get(2).getAsFloat();
                String name=e.has("gem")?"gem_"+e.get("gem").getAsInt():"metal_"+(metal++);
                head.addOrReplaceChild(name,CubeListBuilder.create().texOffs(uv.get(0).getAsInt(),uv.get(1).getAsInt()).addBox(x,y,z,dx,dy,dz),PartPose.ZERO);
            }
        }catch(IOException|RuntimeException e){throw new IllegalStateException("Cannot read crown geometry",e);}
        return new HumanoidModel<>(LayerDefinition.create(mesh,256,256).bakeRoot());
    }
}

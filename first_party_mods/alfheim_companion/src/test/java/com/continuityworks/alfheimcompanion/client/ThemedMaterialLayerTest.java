package com.continuityworks.alfheimcompanion.client;

import com.mojang.blaze3d.vertex.PoseStack;
import java.util.*;
import net.minecraft.client.model.*;
import net.minecraft.client.model.geom.ModelPart;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class ThemedMaterialLayerTest {
    @Test void allOutfitsBakeAndStylesHaveDifferentGeometry() {
        for(String species:List.of("zombie","skeleton","pillager","enderman","endermite"))
            for(int theme=0;theme<8;theme++) {
                Set<String> shapes=new HashSet<>();
                for(int style=0;style<3;style++) {
                    ModelPart root=ThemedMaterialLayer.mesh(species,theme,style).bakeRoot();
                    List<String> geometry=new ArrayList<>();
                    root.visit(new PoseStack(),(pose,path,index,cube)-> {
                        assertTrue(cube.maxX>cube.minX && cube.maxY>cube.minY && cube.maxZ>cube.minZ,path);
                        assertTrue(Float.isFinite(cube.maxX+cube.maxY+cube.maxZ),path);
                        geometry.add(path+":"+cube.minX+","+cube.minY+","+cube.minZ+","+cube.maxX+","+cube.maxY+","+cube.maxZ);
                    });
                    assertFalse(geometry.isEmpty());Collections.sort(geometry);shapes.add(geometry.toString());
                    if(species.equals("endermite")) for(int i=0;i<4;i++) assertTrue(root.hasChild("segment"+i));
                    else for(String part:List.of("head","body","right_arm","left_arm","right_leg","left_leg")) assertTrue(root.hasChild(part));
                }
                assertEquals(3,shapes.size(),species+" theme "+theme+" must have three physical outfits");
            }
    }
    @Test void nonHumanoidAttachmentsExistOnVanillaRigs() {
        ModelPart illager=IllagerModel.createBodyLayer().bakeRoot();
        for(String part:List.of("head","body","right_arm","left_arm","right_leg","left_leg")) assertTrue(illager.hasChild(part),part);
        ModelPart mite=EndermiteModel.createBodyLayer().bakeRoot();
        for(int i=0;i<4;i++) assertTrue(mite.hasChild("segment"+i));
    }
    @Test void pillagerBreastplatesAreOutsideTheSixPixelDeepVanillaTorso() {
        for(int theme=0;theme<8;theme++) for(int style=0;style<3;style++) {
            var root=ThemedMaterialLayer.mesh("pillager",theme,style).bakeRoot();
            boolean[] front={false};
            root.getChild("body").visit(new PoseStack(),(pose,path,index,cube)-> {
                if(cube.minZ < -3.1F) front[0]=true;
            });
            assertTrue(front[0],"Outfit must not be swallowed inside the deeper illager torso");
        }
    }
    @Test void miteShellsTouchTheirAnimatedSegmentAnchor() {
        for(int theme=0;theme<8;theme++) for(int style=0;style<3;style++) {
            var root=ThemedMaterialLayer.mesh("endermite",theme,style).bakeRoot();
            for(int i=0;i<4;i++) root.getChild("segment"+i).getChild("shell").visit(new PoseStack(),(pose,path,index,cube)-> {
                assertTrue(cube.minY<0 && cube.maxY>0,"Shell must touch the segment, not float above it");
            });
        }
    }
}

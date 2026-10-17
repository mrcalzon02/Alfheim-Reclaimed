package com.continuityworks.alfheimcompanion.client;

import com.continuityworks.alfheimcompanion.enemy.EnemyProfiles;
import com.google.gson.*;
import com.mojang.blaze3d.vertex.PoseStack;
import java.nio.file.*;
import java.util.*;
import net.minecraft.client.model.*;
import net.minecraft.client.model.geom.ModelPart;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class RegionalMonstrositiesTest {
    @Test void regionDispatchAndNativeAnimationChannelsRemainCompatible() {
        Set<String> silhouettes=new HashSet<>();
        for(String species:RegionalMonstrosityModels.SPECIES) {
            var root=RegionalMonstrosityModels.layer(species).bakeRoot();
            for(String part:List.of("head","body","left_arm","right_arm","left_leg","right_leg"))assertTrue(root.hasChild(part));
            switch(species) {
                case "zombie" -> new ZombieModel<>(root);
                case "pillager" -> {new IllagerModel<>(root);assertTrue(root.hasChild("arms"));assertTrue(root.getChild("head").hasChild("hat"));}
                case "enderman" -> new EndermanModel<>(root);
            }
            int selected=0;for(int p=0;p<EnemyProfiles.ALL.length;p++)if(RegionalMonstrosityModels.matches(species,p))selected++;
            assertEquals(1,selected,"One habitat per regional body");
            List<String> bounds=new ArrayList<>();root.visit(new PoseStack(),(pose,path,index,cube)-> {
                assertTrue(cube.maxX>cube.minX && cube.maxY>cube.minY && cube.maxZ>cube.minZ,path);
                assertTrue(Float.isFinite(cube.maxX+cube.maxY+cube.maxZ));
                bounds.add(path+":"+cube.minX+","+cube.maxX+","+cube.minY+","+cube.maxY);
            });
            Collections.sort(bounds);assertTrue(silhouettes.add(bounds.toString()));
        }
        assertFalse(RegionalMonstrosityModels.matches("skeleton",13));
    }
    @Test void exportFullBodyReviewModelsFromTheActualBakedGeometry() throws Exception {
        JsonObject review=new JsonObject();
        for(String species:RegionalMonstrosityModels.SPECIES) {
            ModelPart root=RegionalMonstrosityModels.layer(species).bakeRoot();
            JsonArray elements=new JsonArray();
            if(species.equals("pillager")) {
                // ModelPart.visit traverses hidden cubes too. Export only the active
                // open-arm pose, rather than drawing crossed and weapon arms together.
                for(String part:List.of("head","body","right_arm","left_arm","right_leg","left_leg"))
                    EnemyHeadModelsTest.append(elements,root.getChild(part),"base",false);
            } else EnemyHeadModelsTest.append(elements,root,"base",false);
            double[] low={1e9,1e9,1e9},high={-1e9,-1e9,-1e9};
            for(var v:elements)for(int i=0;i<3;i++) {
                low[i]=Math.min(low[i],v.getAsJsonObject().getAsJsonArray("from").get(i).getAsDouble());
                high[i]=Math.max(high[i],v.getAsJsonObject().getAsJsonArray("to").get(i).getAsDouble());
            }
            double scale=14/Math.max(high[0]-low[0],Math.max(high[1]-low[1],high[2]-low[2]));
            for(var value:elements)for(String key:List.of("from","to")) {
                var e=value.getAsJsonObject();double[] xyz=new double[3];
                for(int i=0;i<3;i++)xyz[i]=8+(e.getAsJsonArray(key).get(i).getAsDouble()-(low[i]+high[i])/2)*scale;
                e.add(key,EnemyHeadModelsTest.numbers(xyz));
            }
            JsonObject model=new JsonObject(),display=new JsonObject(),gui=new JsonObject();
            model.add("elements",elements);gui.add("rotation",EnemyHeadModelsTest.numbers(10,155,0));
            gui.add("scale",EnemyHeadModelsTest.numbers(.95,.95,.95));display.add("gui",gui);model.add("display",display);
            review.add(species,model);
        }
        Files.writeString(Path.of("build/regional_monster_review_models.json"),new GsonBuilder().setPrettyPrinting().create().toJson(review)+"\n");
    }
}

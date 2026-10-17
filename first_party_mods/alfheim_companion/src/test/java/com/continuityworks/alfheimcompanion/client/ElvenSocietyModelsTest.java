package com.continuityworks.alfheimcompanion.client;

import com.continuityworks.alfheimcompanion.society.*;
import com.google.gson.*;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
import net.minecraft.client.model.*;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class ElvenSocietyModelsTest {
    static JsonObject model(JsonArray elements){
        double[] low={1e9,1e9,1e9},high={-1e9,-1e9,-1e9};
        for(var v:elements)for(int i=0;i<3;i++){
            low[i]=Math.min(low[i],v.getAsJsonObject().getAsJsonArray("from").get(i).getAsDouble());
            high[i]=Math.max(high[i],v.getAsJsonObject().getAsJsonArray("to").get(i).getAsDouble());
        }
        double scale=14/Math.max(high[0]-low[0],Math.max(high[1]-low[1],high[2]-low[2]));
        for(var v:elements)for(String key:List.of("from","to")){
            var e=v.getAsJsonObject();double[] xyz=new double[3];
            for(int i=0;i<3;i++)xyz[i]=8+(e.getAsJsonArray(key).get(i).getAsDouble()-(low[i]+high[i])/2)*scale;
            e.add(key,EnemyHeadModelsTest.numbers(xyz));
        }
        JsonObject m=new JsonObject(),gui=new JsonObject(),display=new JsonObject();
        m.addProperty("parent","minecraft:block/block");m.addProperty("gui_light","front");m.add("elements",elements);
        gui.add("rotation",EnemyHeadModelsTest.numbers(10,155,0));gui.add("scale",EnemyHeadModelsTest.numbers(.9,.9,.9));display.add("gui",gui);m.add("display",display);return m;
    }
    @Test void exportReferenceElfRigsWithIndependentFinery()throws Exception{
        JsonObject catalogue=new JsonObject(),heads=new JsonObject(),bodies=new JsonObject();JsonArray roles=new JsonArray();
        for(int role=0;role<ElvenSociety.IDS.length;role++){
            var root=ElvenSocietyModels.layer(role).bakeRoot();PlayerModel<ElvenCitizenEntity> base=new PlayerModel<>(root,true);
            var wardrobeRoot=ElvenSocietyModels.wardrobe(role).bakeRoot();HumanoidModel<ElvenCitizenEntity> wardrobe=new HumanoidModel<>(wardrobeRoot);
            base.copyPropertiesTo(wardrobe);
            for(int side:new int[]{-1,1}){
                var ear=wardrobeRoot.getChild("head").getChild("ear"+side);
                assertTrue(ear.yRot==0 && ear.zRot*side>0,"ears sweep outward and up");
                assertTrue(ear.getChild("point").getAllParts().count()>0);
            }
            for(String part:List.of("hat","jacket","left_sleeve","right_sleeve","left_pants","right_pants"))assertTrue(root.hasChild(part),part);
            assertEquals(role,ElvenSociety.role(ElvenSociety.IDS[role]));
            JsonObject row=new JsonObject();row.addProperty("id",ElvenSociety.IDS[role]);row.addProperty("name",ElvenSociety.NAMES[role]);
            JsonArray references=new JsonArray();for(int look=0;look<4;look++)references.add(ElvenSociety.baseSkin(role,look));row.add("base_skins",references);roles.add(row);
            JsonArray body=new JsonArray();EnemyHeadModelsTest.append(body,root,"base",false);EnemyHeadModelsTest.append(body,wardrobeRoot,"wardrobe",false);
            bodies.add(ElvenSociety.IDS[role],model(body));
            for(int look=0;look<4;look++){
                JsonArray head=new JsonArray();EnemyHeadModelsTest.append(head,root.getChild("head"),"base",false);
                EnemyHeadModelsTest.append(head,root.getChild("hat"),"base",false);
                EnemyHeadModelsTest.append(head,wardrobeRoot.getChild("head"),"wardrobe",false);
                JsonObject m=model(head),tex=new JsonObject();tex.addProperty("base",ElvenSociety.baseSkin(role,look));
                tex.addProperty("wardrobe","alfheim_companion:entity/society/wardrobe/"+ElvenSociety.IDS[role]+"_"+look);
                tex.addProperty("particle",tex.get("base").getAsString());m.add("textures",tex);
                heads.add(ElvenSociety.IDS[role]+"_"+look,m);
            }
        }
        assertEquals(12,roles.size());assertEquals(48,heads.size());assertEquals(0,ElvenSociety.role("unknown"));
        catalogue.add("roles",roles);catalogue.add("heads",heads);catalogue.add("bodies",bodies);
        for(String source:List.of("client/ElvenSocietyModels.java","society/ElvenSociety.java")){
            Path path=Path.of("src/main/java/com/continuityworks/alfheimcompanion/"+source);
            catalogue.addProperty(source,HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(Files.readAllBytes(path))));
        }
        Files.writeString(Path.of("build/elven_society_geometry.json"),new GsonBuilder().setPrettyPrinting().create().toJson(catalogue)+"\n");
    }
}

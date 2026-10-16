package com.continuityworks.alfheimcompanion.client;

import com.continuityworks.alfheimcompanion.enemy.EnemyProfiles;
import com.google.gson.*;
import com.mojang.blaze3d.vertex.*;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
import net.minecraft.client.model.*;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.builders.*;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

/** Export actual baked head surfaces so inventory assets cannot invent a different creature. */
class EnemyHeadModelsTest {
    static final String[] SPECIES={"zombie","skeleton","pillager","enderman","endermite"};
    static final String[] SKINS={"entity/zombie/zombie","entity/skeleton/skeleton","entity/illager/pillager",
        "entity/enderman/enderman","entity/endermite"};
    record Vertex(double x,double y,double z,float u,float v,float nx,float ny,float nz) {}
    static class Capture implements VertexConsumer {
        List<Vertex> vertices=new ArrayList<>(); double x,y,z;float u,v,nx,ny,nz;
        public VertexConsumer vertex(double x,double y,double z){this.x=x*16;this.y=-y*16;this.z=z*16;return this;}
        public VertexConsumer color(int r,int g,int b,int a){return this;}
        public VertexConsumer uv(float u,float v){this.u=u;this.v=v;return this;}
        public VertexConsumer overlayCoords(int u,int v){return this;}
        public VertexConsumer uv2(int u,int v){return this;}
        public VertexConsumer normal(float x,float y,float z){nx=x;ny=-y;nz=z;return this;}
        public void endVertex(){vertices.add(new Vertex(x,y,z,u,v,nx,ny,nz));}
        public void defaultColor(int r,int g,int b,int a){}
        public void unsetDefaultColor(){}
    }
    static JsonArray numbers(double... values) {
        JsonArray a=new JsonArray();for(double v:values)a.add(Math.rint(v*1e6)/1e6);return a;
    }
    static String direction(Vertex v) {
        return Math.abs(v.nx)>.5 ? (v.nx>0?"east":"west") : Math.abs(v.ny)>.5 ?
            (v.ny>0?"up":"down") : v.nz>0?"south":"north";
    }
    static void append(JsonArray elements,ModelPart part,String texture,boolean material) {
        part.visit(new PoseStack(),(pose,path,index,cube)-> {
            Capture capture=new Capture();cube.compile(pose,capture,0,0,1,1,1,1);
            double[] low={Double.POSITIVE_INFINITY,Double.POSITIVE_INFINITY,Double.POSITIVE_INFINITY};
            double[] high={-Double.POSITIVE_INFINITY,-Double.POSITIVE_INFINITY,-Double.POSITIVE_INFINITY};
            for(Vertex v:capture.vertices) {
                double[] p={v.x,v.y,v.z};for(int i=0;i<3;i++){low[i]=Math.min(low[i],p[i]);high[i]=Math.max(high[i],p[i]);}
            }
            JsonObject faces=new JsonObject();
            for(int i=0;i<capture.vertices.size();i+=4) {
                var quad=capture.vertices.subList(i,i+4);JsonObject face=new JsonObject();face.addProperty("texture","#"+texture);
                if(material){face.add("uv",numbers(0,0,16,16));face.addProperty("tintindex",path.contains("detail")?1:0);}
                else {
                    face.add("uv",numbers(quad.stream().mapToDouble(v->v.u).min().orElseThrow()*16,
                        quad.stream().mapToDouble(v->v.v).min().orElseThrow()*16,
                        quad.stream().mapToDouble(v->v.u).max().orElseThrow()*16,
                        quad.stream().mapToDouble(v->v.v).max().orElseThrow()*16));
                }
                // Accent child geometry uses the same secondary material as the live renderer.
                if(material && path.contains("detail"))face.addProperty("texture","#detail");
                faces.add(direction(quad.get(0)),face);
            }
            JsonObject e=new JsonObject();e.add("from",numbers(low));e.add("to",numbers(high));e.add("faces",faces);elements.add(e);
        });
    }
    static ModelPart base(String species) {
        return switch(species) {
            case "pillager" -> IllagerModel.createBodyLayer().bakeRoot().getChild("head");
            case "enderman" -> EndermanModel.createBodyLayer().bakeRoot().getChild("head");
            case "skeleton" -> SkeletonModel.createBodyLayer().bakeRoot().getChild("head");
            case "endermite" -> EndermiteModel.createBodyLayer().bakeRoot().getChild("segment0");
            default -> LayerDefinition.create(HumanoidModel.createMesh(CubeDeformation.NONE,0),64,64).bakeRoot().getChild("head");
        };
    }
    @Test void exportAllHeadsWithSharedSpeciesGeometry() throws Exception {
        JsonObject catalogue=new JsonObject(),models=new JsonObject();int count=0;
        for(int s=0;s<5;s++) {
            Set<String> shapes=new HashSet<>();
            for(int p=0;p<EnemyProfiles.ALL.length;p++)for(int style=0;style<3;style++) {
                String species=SPECIES[s];var profile=EnemyProfiles.get(p);
                boolean custom=species.equals("skeleton") && p==13 && style==0;
                JsonArray elements=new JsonArray();
                append(elements,custom?SilverbarkBoneguardModel.layer().bakeRoot().getChild("head"):base(species),"base",false);
                double[] low={1e9,1e9,1e9},high={-1e9,-1e9,-1e9};
                List<String> bounds=new ArrayList<>();
                for(var value:elements) {
                    var e=value.getAsJsonObject();bounds.add(e.get("from").toString()+e.get("to"));
                    for(int i=0;i<3;i++){low[i]=Math.min(low[i],e.getAsJsonArray("from").get(i).getAsDouble());high[i]=Math.max(high[i],e.getAsJsonArray("to").get(i).getAsDouble());}
                }
                Collections.sort(bounds);shapes.add(bounds.toString());
                double scale=14/Math.max(high[0]-low[0],Math.max(high[1]-low[1],high[2]-low[2]));
                for(var value:elements)for(String key:List.of("from","to")) {
                    var e=value.getAsJsonObject();double[] v=new double[3];
                    for(int i=0;i<3;i++)v[i]=8+(e.getAsJsonArray(key).get(i).getAsDouble()-(low[i]+high[i])/2)*scale;
                    e.add(key,numbers(v));
                }
                JsonObject model=new JsonObject(),textures=new JsonObject(),display=new JsonObject(),gui=new JsonObject();
                textures.addProperty("base","alfheim_companion:entity/themed/"+species+"_"+p+"_"+style);
                textures.addProperty("body",profile.texture().toString().replace("textures/","").replace(".png",""));
                textures.addProperty("detail",profile.detailTexture().toString().replace("textures/","").replace(".png",""));
                textures.addProperty("particle","minecraft:"+SKINS[s]);
                model.addProperty("parent","minecraft:block/block");model.addProperty("gui_light","front");
                model.add("textures",textures);model.add("elements",elements);
                gui.add("rotation",numbers(15,155,0));gui.add("translation",numbers(0,0,0));gui.add("scale",numbers(.85,.85,.85));
                display.add("gui",gui);model.add("display",display);
                models.add(species+"_"+p+"_"+style,model);count++;
            }
            assertEquals(SPECIES[s].equals("skeleton")?2:1,shapes.size(),SPECIES[s]);
        }
        assertEquals(390,count);catalogue.add("models",models);
        Path source=Path.of("src/main/java/com/continuityworks/alfheimcompanion/client/ThemedMaterialLayer.java");
        catalogue.addProperty("layer_sha256",HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(Files.readAllBytes(source))));
        Path exporter=Path.of("src/test/java/com/continuityworks/alfheimcompanion/client/EnemyHeadModelsTest.java");
        catalogue.addProperty("exporter_sha256",HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(Files.readAllBytes(exporter))));
        Path out=Path.of("build/themed_head_models.json");Files.createDirectories(out.getParent());
        Files.writeString(out,new GsonBuilder().setPrettyPrinting().create().toJson(catalogue)+"\n");
    }
}

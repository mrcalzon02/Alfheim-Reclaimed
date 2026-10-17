package com.continuityworks.alfheimcompanion.client;

import com.continuityworks.alfheimcompanion.monstrosity.*;
import com.google.gson.*;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.model.geom.ModelPart;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class MonstrosityModelsTest {
    static JsonArray mesh(ModelPart root,java.util.List<MonstrosityModel.Surface> surfaces){
        var quads=new JsonArray();
        root.visit(new PoseStack(),(pose,path,index,cube)->{
            var capture=new EnemyHeadModelsTest.Capture();cube.compile(pose,capture,0,0,1,1,1,1);
            for(int i=0;i<capture.vertices.size();i+=4){
                var q=new JsonObject();var vertices=new JsonArray();var uv=new JsonArray();
                for(var v:capture.vertices.subList(i,i+4)){
                    vertices.add(EnemyHeadModelsTest.numbers(v.x(),v.y(),v.z()));uv.add(EnemyHeadModelsTest.numbers(v.u(),v.v()));
                }
                var v=capture.vertices.get(i);q.add("vertices",vertices);q.add("uv",uv);
                double centerU=capture.vertices.subList(i,i+4).stream().mapToDouble(a->a.u()).average().orElseThrow()*MonstrosityModel.ATLAS_SIZE;
                double centerV=capture.vertices.subList(i,i+4).stream().mapToDouble(a->a.v()).average().orElseThrow()*MonstrosityModel.ATLAS_SIZE;
                var surface=surfaces.stream().filter(a->centerU>=a.u()&&centerU<=a.u()+a.width()&&centerV>=a.v()&&centerV<=a.v()+a.height()).findFirst().orElseThrow();
                q.addProperty("material",surface.material());q.addProperty("part",surface.name());q.addProperty("face",i/4);q.add("normal",EnemyHeadModelsTest.numbers(v.nx(),v.ny(),v.nz()));quads.add(q);
            }
        });return quads;
    }
    @Test void exportDistinctAnatomiesAndMatchingInventoryHeads()throws Exception{
        var catalogue=new JsonObject();var models=new JsonObject();var heads=new JsonObject();var rows=new JsonArray();
        var shapes=new HashSet<String>();
        for(var kind:MonstrosityKind.values()){
            var root=MonstrosityModel.layer(kind).bakeRoot();var model=new MonstrosityModel(root,kind);
            var shape=new ArrayList<String>();
            for(int frame=0;frame<40;frame++){
                model.setupAnim(null,frame*.3F,.75F,frame,25,-10);
                root.getAllParts().forEach(part->assertTrue(Float.isFinite(part.xRot+part.yRot+part.zRot)));
            }
            root.getAllParts().forEach(ModelPart::resetPose);
            root.visit(new PoseStack(),(pose,path,index,cube)->{
                assertTrue(cube.maxX>cube.minX&&cube.maxY>cube.minY&&cube.maxZ>cube.minZ,path);
                shape.add(path+cube.minX+","+cube.minY+","+cube.minZ+":"+cube.maxX+","+cube.maxY+","+cube.maxZ);
            });
            assertTrue(shapes.add(shape.toString()),"Each species has its own silhouette");
            if(kind==MonstrosityKind.CYCLOPS){assertTrue(root.getChild("head").hasChild("single_iris"));assertFalse(root.getChild("head").hasChild("eye_left"));}
            if(kind==MonstrosityKind.INFESTOR)assertTrue(root.getChild("right_arm").getChild("whip_middle").hasChild("whip_tip"));
            models.add(kind.id,mesh(root,MonstrosityModel.surfaces()));
            heads.add(kind.id,mesh(root.getChild("head"),MonstrosityModel.surfaces()));
            var row=new JsonObject();row.addProperty("id",kind.id);row.addProperty("label",kind.label);row.addProperty("height",kind.height);
            row.addProperty("width",kind.width);var names=new JsonArray();for(String name:kind.variants)names.add(name);row.add("variants",names);rows.add(row);
        }
        assertEquals(3.6F,MonstrosityKind.TROLL.height);assertEquals(MonstrosityKind.values().length,shapes.size());
        assertEquals(19,shapes.size());
        catalogue.addProperty("atlas_size",MonstrosityModel.ATLAS_SIZE);catalogue.add("models",models);catalogue.add("heads",heads);catalogue.add("species",rows);
        for(String source:List.of("client/MonstrosityModel.java","monstrosity/MonstrosityKind.java")){
            Path p=Path.of("src/main/java/com/continuityworks/alfheimcompanion/"+source);
            catalogue.addProperty(source,HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(Files.readAllBytes(p))));
        }
        Files.writeString(Path.of("build/monstrosity_geometry.json"),new GsonBuilder().setPrettyPrinting().create().toJson(catalogue)+"\n");
    }
}

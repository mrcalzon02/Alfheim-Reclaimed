package com.continuityworks.alfheimcompanion.worldgen;

import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructurePlaceSettings;

/** Fitted CW-authored interiors. Existing graph, boundary walls and site ownership remain authoritative. */
public final class ActOneAuthoredInteriors {
    public static final String[] SERVICES={"arms","provisions","apothecary","repair","supplies","salvage"};
    private static final String[] ROOMS={"monastery_vestibule","ruined_nave","bone_cloister","novices_cells",
        "ossuary","spider_gallery","bell_chamber","scriptorium","reliquary","cistern","refectory",
        "grave_gallery","ritual_chapel","descent_hub","elite_arena","boss_sanctuary","return_shrine"};
    public static void place(WorldGenLevel world,String kind,int variant,BoundingBox piece,BoundingBox chunk,RandomSource random){
        if(kind.equals("village")){
            int i=0;
            for(int x:new int[]{6,27,48})for(int z:new int[]{5,49}){
                var at=new BlockPos(piece.minX()+x,piece.minY(),piece.minZ()+z);
                placeOne(world,"ashen_refuge/"+SERVICES[i++],at,chunk,random,false);
            }
        }else if(kind.equals("room")&&variant%9!=4){
            // Central hubs own the permanent descent shaft; never furnish over that route.
            var inner=new BoundingBox(piece.minX()+2,piece.minY(),piece.minZ()+2,
                piece.maxX()-2,piece.minY()+13,piece.maxZ()-2);
            var crop=intersection(inner,chunk);
            if(crop!=null)placeOne(world,"ashen_cloister/"+ROOMS[Math.floorMod(variant,ROOMS.length)],
                new BlockPos(piece.minX(),piece.minY(),piece.minZ()),crop,random,true);
        }
    }
    private static BoundingBox intersection(BoundingBox a,BoundingBox b){
        int x=Math.max(a.minX(),b.minX()),y=Math.max(a.minY(),b.minY()),z=Math.max(a.minZ(),b.minZ());
        int xx=Math.min(a.maxX(),b.maxX()),yy=Math.min(a.maxY(),b.maxY()),zz=Math.min(a.maxZ(),b.maxZ());
        return x>xx||y>yy||z>zz?null:new BoundingBox(x,y,z,xx,yy,zz);
    }
    private static void placeOne(WorldGenLevel world,String path,BlockPos at,BoundingBox crop,RandomSource random,boolean ignoreEntities){
        var id=new ResourceLocation("alfheim",path);
        var template=world.getLevel().getStructureManager().get(id).orElseThrow(()->new IllegalStateException("Missing authored interior "+id));
        var settings=new StructurePlaceSettings().setBoundingBox(crop).setIgnoreEntities(ignoreEntities);
        template.placeInWorld(world,at,at,settings,random,2);
    }
    private ActOneAuthoredInteriors(){}
}

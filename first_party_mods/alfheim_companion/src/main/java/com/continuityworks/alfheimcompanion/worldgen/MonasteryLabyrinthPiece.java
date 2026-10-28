package com.continuityworks.alfheimcompanion.worldgen;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.StructureManager;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.LadderBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.StructurePiece;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext;

/**
 * Bounded, chunk-local structural geometry. Each room is <=29 blocks wide;
 * native pieces avoid a giant jigsaw's 128-block expansion limit.
 *
 * Initial playable topology uses permanent vertical ladders; the graph keeps
 * vertical_stair edges so authored switchback stairs can replace them later.
 * Vendor stalls and bosses have RESERVED positions, not fake NPC/mob spawns.
 */
public final class MonasteryLabyrinthPiece extends StructurePiece {
    private final String kind;
    private final int act,mask,variant;
    public MonasteryLabyrinthPiece(String kind,int act,int mask,int variant,
            int x,int y,int z,int width,int height,int depth){
        super(ModHarborStructures.LABYRINTH_PIECE.get(),0,
            new BoundingBox(x,y,z,x+width-1,y+height-1,z+depth-1));
        this.kind=kind;this.act=act;this.mask=mask;this.variant=variant;
    }
    public MonasteryLabyrinthPiece(CompoundTag tag){
        super(ModHarborStructures.LABYRINTH_PIECE.get(),tag);
        kind=tag.getString("LKind");act=tag.getInt("LAct");
        mask=tag.getInt("LMask");variant=tag.getInt("LVariant");
    }
    @Override protected void addAdditionalSaveData(StructurePieceSerializationContext context,CompoundTag tag){
        tag.putString("LKind",kind);tag.putInt("LAct",act);
        tag.putInt("LMask",mask);tag.putInt("LVariant",variant);
    }
    private BlockState stone(){
        return switch(act){
            case 2 -> Blocks.CUT_SANDSTONE.defaultBlockState();
            case 3 -> Blocks.MUD_BRICKS.defaultBlockState();
            case 4 -> Blocks.NETHER_BRICKS.defaultBlockState();
            case 5 -> Blocks.DEEPSLATE_BRICKS.defaultBlockState();
            default -> Blocks.MOSSY_STONE_BRICKS.defaultBlockState();
        };
    }
    private BlockState trim(){
        return switch(act){
            case 2 -> Blocks.CHISELED_SANDSTONE.defaultBlockState();
            case 3 -> Blocks.MOSSY_COBBLESTONE.defaultBlockState();
            case 4 -> Blocks.CHISELED_NETHER_BRICKS.defaultBlockState();
            case 5 -> Blocks.POLISHED_DEEPSLATE.defaultBlockState();
            default -> Blocks.CRACKED_STONE_BRICKS.defaultBlockState();
        };
    }
    private BlockState paving(){
        return switch(act){
            case 2 -> Blocks.SMOOTH_SANDSTONE.defaultBlockState();
            case 3 -> Blocks.MUD_BRICKS.defaultBlockState();
            case 4 -> Blocks.POLISHED_BLACKSTONE_BRICKS.defaultBlockState();
            case 5 -> Blocks.POLISHED_DEEPSLATE.defaultBlockState();
            default -> Blocks.STONE_BRICKS.defaultBlockState();
        };
    }
    private boolean door(int x,int y,int z,int w,int d){
        if(y<2 || y>6)return false;
        if(x>=w/2-2 && x<=w/2+2){
            if(z<=1 && (mask&1)!=0)return true;
            if(z>=d-2 && (mask&4)!=0)return true;
        }
        if(z>=d/2-2 && z<=d/2+2){
            if(x>=w-2 && (mask&2)!=0)return true;
            if(x<=1 && (mask&8)!=0)return true;
        }
        return false;
    }
    private BlockState room(int x,int y,int z,int w,int d){
        if(y<=1)return paving();
        if(y==14)return trim();
        if(x<2||z<2||x>=w-2||z>=d-2)
            return door(x,y,z,w,d)?Blocks.AIR.defaultBlockState():stone();
        // Four structural columns frame each hall; light is architectural,
        // not a sea of floating torches or generic block piles.
        if((x==4||x==w-5)&&(z==4||z==d-5)){
            if(y==11)return Blocks.SEA_LANTERN.defaultBlockState();
            return trim();
        }
        if(variant%9==4 && y==2 && x>=12 && x<=16 && z>=12 && z<=16)
            return trim(); // boss/hub central floor insignia
        return Blocks.AIR.defaultBlockState();
    }
    private BlockState corridor(int x,int y,int z,int w,int d){
        if(y<=1)return paving();
        if(y==7)return stone();
        boolean border=kind.equals("corridor_x")?(z==0||z==d-1):(x==0||x==w-1);
        if(border)return stone();
        if(y==6 && ((kind.equals("corridor_x")?x:z)%9)==0)
            return Blocks.SEA_LANTERN.defaultBlockState();
        return Blocks.AIR.defaultBlockState();
    }
    private BlockState shaft(int x,int y,int z,int w,int h,int d){
        if(y<=1)return paving();
        // North backing wall supports ladders continuously to the upper room.
        if(x==3 && z==1 && y<h-2)
            return Blocks.LADDER.defaultBlockState().setValue(LadderBlock.FACING,Direction.SOUTH);
        boolean upper=y>=h-8,lower=y<=6;
        if((x==0||x==w-1) && z>=2&&z<=4 && (upper||lower))
            return Blocks.AIR.defaultBlockState();
        if(x==0||z==0||x==w-1||z==d-1)return stone();
        return Blocks.AIR.defaultBlockState();
    }
    private BlockState monastery(int x,int y,int z,int w,int d){
        boolean nave=x>=6&&x<=58&&z>=6&&z<=58;
        if(!nave)return null;
        if(y<=3)return stone();
        if(y==4)return paving();
        boolean wall=x<=7||x>=57||z<=7||z>=57;
        boolean eastDoor=x>=57&&z>=29&&z<=35&&y<=11;
        boolean northDoor=z<=7&&x>=29&&x<=35&&y<=11;
        if(wall) {
            if(eastDoor||northDoor)return Blocks.AIR.defaultBlockState();
            if(y>=11&&y<=15&&((x+z)%8<=2))return Blocks.IRON_BARS.defaultBlockState();
            return y<=23?stone():null;
        }
        if(y==23)return trim();
        if(y==22&&(x%7==0||z%7==0))return stone();
        if(y>=5&&y<22) {
            if((x==12||x==52)&&(z==12||z==52)&&y<=20)return trim();
            if(y==6&&((x==12&&z==32)||(x==52&&z==32)))return Blocks.LANTERN.defaultBlockState();
            if(y==5 && z==13 && x>=28&&x<=36)return trim();
            return Blocks.AIR.defaultBlockState();
        }
        return null;
    }
    private BlockState village(int x,int y,int z,int w,int d){
        return switch(MonasteryVillageGeometry.village(x,y,z)){
            case NONE -> null;
            case FOUNDATION,WALL -> stone();
            case PAVING -> paving();
            case ROAD_TRIM,ROOF -> trim();
            case AIR -> Blocks.AIR.defaultBlockState();
            case FENCE -> Blocks.OAK_FENCE.defaultBlockState();
            case LIGHT -> Blocks.SEA_LANTERN.defaultBlockState();
            case BARREL -> Blocks.BARREL.defaultBlockState();
        };
    }
    private BlockState approach(int x,int y,int z,int w,int d){
        return switch(MonasteryVillageGeometry.approach(y)){
            case FOUNDATION -> stone();
            case PAVING -> paving();
            case AIR -> Blocks.AIR.defaultBlockState();
            default -> null;
        };
    }
    @Override public void postProcess(WorldGenLevel world,StructureManager manager,
            ChunkGenerator generator,RandomSource random,BoundingBox chunk,ChunkPos chunkPos,BlockPos pivot){
        int x0=boundingBox.minX(),y0=boundingBox.minY(),z0=boundingBox.minZ();
        int w=boundingBox.maxX()-x0+1,h=boundingBox.maxY()-y0+1,d=boundingBox.maxZ()-z0+1;
        var at=new BlockPos.MutableBlockPos();
        for(int x=Math.max(x0,chunk.minX());x<=Math.min(boundingBox.maxX(),chunk.maxX());x++)
            for(int z=Math.max(z0,chunk.minZ());z<=Math.min(boundingBox.maxZ(),chunk.maxZ());z++)
                for(int y=Math.max(y0,chunk.minY());y<=Math.min(boundingBox.maxY(),chunk.maxY());y++){
                    int lx=x-x0,ly=y-y0,lz=z-z0;
                    BlockState state=switch(kind){
                        case "room" -> room(lx,ly,lz,w,d);
                        case "corridor_x","corridor_z" -> corridor(lx,ly,lz,w,d);
                        case "shaft" -> shaft(lx,ly,lz,w,h,d);
                        case "monastery" -> monastery(lx,ly,lz,w,d);
                        case "village" -> village(lx,ly,lz,w,d);
                        case "approach" -> approach(lx,ly,lz,w,d);
                        default -> null;
                    };
                    if(state!=null){at.set(x,y,z);world.setBlock(at,state,2);}
                }
    }
}

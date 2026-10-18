package com.continuityworks.alfheimcompanion.worldgen;

import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.BlockTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.StructureManager;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.StructurePiece;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext;

/** Saved, chunk-clipped foundation apron and shallow soil transition before authored templates. */
public final class GroundPlatePiece extends StructurePiece implements net.minecraftforge.common.world.PieceBeardifierModifier {
    private final int minX,minZ,maxX,maxZ,top,edge,feather,depth;
    private final boolean water;
    private final String material;
    public GroundPlatePiece(int x0,int z0,int x1,int z1,int top,TerrainAffordances.Profile p){
        super(ModHarborStructures.GROUND_PLATE.get(),0,new BoundingBox(x0-p.halo(),top-p.depth(),z0-p.halo(),x1+p.halo(),top,z1+p.halo()));
        minX=x0;minZ=z0;maxX=x1;maxZ=z1;this.top=top;edge=p.edge();feather=p.feather();depth=p.depth();water=p.water();material=p.material();
    }
    public GroundPlatePiece(CompoundTag t){
        super(ModHarborStructures.GROUND_PLATE.get(),t);
        minX=t.getInt("PlateMinX");minZ=t.getInt("PlateMinZ");maxX=t.getInt("PlateMaxX");maxZ=t.getInt("PlateMaxZ");
        top=t.getInt("PlateY");edge=t.getInt("Edge");feather=t.getInt("Feather");depth=t.getInt("Depth");water=t.getBoolean("Water");material=t.getString("Material");
    }
    @Override protected void addAdditionalSaveData(StructurePieceSerializationContext c,CompoundTag t){
        t.putInt("PlateMinX",minX);t.putInt("PlateMinZ",minZ);t.putInt("PlateMaxX",maxX);t.putInt("PlateMaxZ",maxZ);
        t.putInt("PlateY",top);t.putInt("Edge",edge);t.putInt("Feather",feather);t.putInt("Depth",depth);t.putBoolean("Water",water);t.putString("Material",material);
    }
    public static int distance(int x,int z,int x0,int z0,int x1,int z1){return Math.max(Math.max(x0-x,x-x1),Math.max(Math.max(z0-z,z-z1),0));}
    public static int capY(int top,int distance,int edge){return top-Math.max(0,distance-edge);}
    // The authored jigsaw pieces already supply the terrain blend. A second
    // beard at the bottom of these footings can excavate a gap beneath them.
    @Override public BoundingBox getBeardifierBox(){return boundingBox;}
    @Override public net.minecraft.world.level.levelgen.structure.TerrainAdjustment getTerrainAdjustment(){return net.minecraft.world.level.levelgen.structure.TerrainAdjustment.NONE;}
    @Override public int getGroundLevelDelta(){return 0;}
    @Override public void postProcess(WorldGenLevel world,StructureManager manager,ChunkGenerator generator,RandomSource random,BoundingBox chunk,ChunkPos pos,BlockPos pivot){
        var id=new ResourceLocation(material);
        if(!BuiltInRegistries.BLOCK.containsKey(id))throw new IllegalStateException("Unknown foundation material "+id);
        var stone=BuiltInRegistries.BLOCK.get(id).defaultBlockState();var at=new BlockPos.MutableBlockPos();
        for(int x=Math.max(chunk.minX(),boundingBox.minX());x<=Math.min(chunk.maxX(),boundingBox.maxX());x++)
            for(int z=Math.max(chunk.minZ(),boundingBox.minZ());z<=Math.min(chunk.maxZ(),boundingBox.maxZ());z++){
                int distance=distance(x,z,minX,minZ,maxX,maxZ),cap=capY(top,distance,edge);
                boolean shoulder=distance>edge;
                // Feather only into dry, empty space. It never dams a water channel.
                at.set(x,cap,z);var original=world.getBlockState(at);
                if(shoulder&&(!original.getFluidState().isEmpty()||original.isCollisionShapeFullBlock(world,at)))continue;
                for(int y=cap;y>=Math.max(world.getMinBuildHeight()+1,top-depth);y--){
                    at.set(x,y,z);var old=world.getBlockState(at);
                    if(world.getBlockEntity(at)!=null)break;
                    if(!water&&!old.getFluidState().isEmpty())break;
                    boolean solid=!old.is(BlockTags.LEAVES)&&!old.is(BlockTags.LOGS)&&old.isCollisionShapeFullBlock(world,at);
                    if(solid)break; // Preserve all buried solid terrain, ores and other structures.
                    if(chunk.isInside(at))world.setBlock(at,shoulder?(y==cap?Blocks.GRASS_BLOCK:Blocks.DIRT).defaultBlockState():stone,2);
                }
            }
    }
}

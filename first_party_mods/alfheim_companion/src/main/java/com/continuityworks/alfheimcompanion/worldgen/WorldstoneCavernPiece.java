package com.continuityworks.alfheimcompanion.worldgen;

import com.continuityworks.alfheimcompanion.worldstone.ModWorldstoneBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.AmethystClusterBlock;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.*;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext;

/** Writes only the currently generating chunk. No force loads, entities or runtime tick scans. */
public final class WorldstoneCavernPiece extends StructurePiece {
    private final int centreX,centreZ;
    public WorldstoneCavernPiece(int x,int z) {
        super(ModHarborStructures.WORLDSTONE_PIECE.get(),0,new BoundingBox(x-119,-48,z-119,x+119,168,z+119));centreX=x;centreZ=z;
    }
    public WorldstoneCavernPiece(CompoundTag tag){super(ModHarborStructures.WORLDSTONE_PIECE.get(),tag);centreX=tag.getInt("CentreX");centreZ=tag.getInt("CentreZ");}
    @Override protected void addAdditionalSaveData(StructurePieceSerializationContext c,CompoundTag tag){tag.putInt("CentreX",centreX);tag.putInt("CentreZ",centreZ);}
    @Override public void postProcess(WorldGenLevel world,StructureManager manager,ChunkGenerator generator,
            RandomSource random,BoundingBox chunk,ChunkPos chunkPos,BlockPos pivot) {
        var dark=BuiltInRegistries.BLOCK.get(new ResourceLocation("alfheim","obsidian_livingrock")).defaultBlockState();
        var cracked=BuiltInRegistries.BLOCK.get(new ResourceLocation("alfheim","cracked_livingrock")).defaultBlockState();
        var fleck=BuiltInRegistries.BLOCK.get(new ResourceLocation("alfheim","starfleck_livingrock")).defaultBlockState();
        var crystal=ModWorldstoneBlocks.CRYSTAL.get().defaultBlockState();var heart=ModWorldstoneBlocks.HEART.get().defaultBlockState();
        var air=Blocks.CAVE_AIR.defaultBlockState();var at=new BlockPos.MutableBlockPos();
        for(int x=Math.max(chunk.minX(),boundingBox.minX());x<=Math.min(chunk.maxX(),boundingBox.maxX());x++)
            for(int z=Math.max(chunk.minZ(),boundingBox.minZ());z<=Math.min(chunk.maxZ(),boundingBox.maxZ());z++) {
                // Per-column final cap protects missed terrain dips between the noise probes.
                int cap=Math.min(boundingBox.maxY(),world.getHeight(Heightmap.Types.OCEAN_FLOOR_WG,x,z)-WorldstoneLayout.ROOF);
                int dx=x-centreX,dz=z-centreZ;
                for(int y=Math.max(chunk.minY(),boundingBox.minY());y<=Math.min(chunk.maxY(),cap);y++) {
                    double q=WorldstoneLayout.density(dx,y,dz);if(q>1.065)continue;
                    int material=WorldstoneLayout.crystal(dx,y,dz);
                    var stone=Math.floorMod(Math.floorDiv(dx,13)+Math.floorDiv(dz,17)+Math.floorDiv(y,9),9)==0?fleck:
                        Math.floorMod(dx+dz+y,13)<3?cracked:dark;
                    var desired=q>=1 || WorldstoneLayout.shelf(dx,y,dz)?stone:material==1?crystal:material==2?heart:air;
                    if(q>=1 && WorldstoneLayout.ore(dx,y,dz))desired=ModWorldstoneBlocks.ORE.get().defaultBlockState();
                    if(desired==air) {
                        int facing=WorldstoneLayout.seedFace(dx,y,dz);
                        if(facing>=0)desired=ModWorldstoneBlocks.CLUSTER.get().defaultBlockState().setValue(AmethystClusterBlock.FACING,Direction.values()[facing]);
                    }
                    at.set(x,y,z);var old=world.getBlockState(at);
                    if(old.is(Blocks.BEDROCK) || old.hasBlockEntity() || old==desired)continue;
                    world.setBlock(at,desired,2);
                }
            }
    }
}

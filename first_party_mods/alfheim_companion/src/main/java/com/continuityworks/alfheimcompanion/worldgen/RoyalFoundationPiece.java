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
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.StructurePiece;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext;

/** Fills only missing support, at most 96 blocks down, within the current generation chunk. */
public final class RoyalFoundationPiece extends StructurePiece {
    public RoyalFoundationPiece(int x,int y,int z) {super(ModHarborStructures.ROYAL_FOUNDATION.get(),0,new BoundingBox(x,y-96,z,x+234,y+7,z+234));}
    public RoyalFoundationPiece(CompoundTag tag) {super(ModHarborStructures.ROYAL_FOUNDATION.get(),tag);}
    @Override protected void addAdditionalSaveData(StructurePieceSerializationContext c,CompoundTag tag) {}
    @Override public void postProcess(WorldGenLevel world,StructureManager manager,ChunkGenerator generator,
            RandomSource random,BoundingBox chunk,ChunkPos chunkPos,BlockPos pivot) {
        var stone=BuiltInRegistries.BLOCK.get(new ResourceLocation("alfheim","ivory_livingrock_bricks")).defaultBlockState();
        var at=new BlockPos.MutableBlockPos();
        for(int x=Math.max(chunk.minX(),boundingBox.minX());x<=Math.min(chunk.maxX(),boundingBox.maxX());x++)
            for(int z=Math.max(chunk.minZ(),boundingBox.minZ());z<=Math.min(chunk.maxZ(),boundingBox.maxZ());z++)
                for(int y=boundingBox.maxY();y>=Math.max(world.getMinBuildHeight()+1,boundingBox.minY());y--) {
                    at.set(x,y,z);var old=world.getBlockState(at);
                    if(!old.is(BlockTags.LEAVES) && !old.is(BlockTags.LOGS) && old.isCollisionShapeFullBlock(world,at))break;
                    if(chunk.isInside(at))world.setBlock(at,stone,2);
                }
    }
}

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
    private final int coreX,coreZ,base;
    public RoyalFoundationPiece(int x,int y,int z) {
        super(ModHarborStructures.ROYAL_FOUNDATION.get(),0,new BoundingBox(x-1,y-96,z-1,x+235,y+7,z+235));
        coreX=x;coreZ=z;base=y;
    }
    public RoyalFoundationPiece(CompoundTag tag) {
        super(ModHarborStructures.ROYAL_FOUNDATION.get(),tag);
        coreX=tag.contains("CoreX")?tag.getInt("CoreX"):boundingBox.minX();
        coreZ=tag.contains("CoreZ")?tag.getInt("CoreZ"):boundingBox.minZ();
        base=tag.contains("BaseY")?tag.getInt("BaseY"):boundingBox.maxY()-7;
    }
    @Override protected void addAdditionalSaveData(StructurePieceSerializationContext c,CompoundTag tag) {
        tag.putInt("CoreX",coreX);tag.putInt("CoreZ",coreZ);tag.putInt("BaseY",base);
    }
    @Override public void postProcess(WorldGenLevel world,StructureManager manager,ChunkGenerator generator,
            RandomSource random,BoundingBox chunk,ChunkPos chunkPos,BlockPos pivot) {
        var stone=BuiltInRegistries.BLOCK.get(new ResourceLocation("alfheim","ivory_livingrock_bricks")).defaultBlockState();
        var at=new BlockPos.MutableBlockPos();
        for(int x=Math.max(chunk.minX(),boundingBox.minX());x<=Math.min(chunk.maxX(),boundingBox.maxX());x++)
            for(int z=Math.max(chunk.minZ(),boundingBox.minZ());z<=Math.min(chunk.maxZ(),boundingBox.maxZ());z++) {
                boolean apron=x<coreX||x>coreX+234||z<coreZ||z>coreZ+234;
                boolean gate=apron&&((Math.abs(x-(coreX+117))<=4&&(z<coreZ||z>coreZ+234))
                    ||(Math.abs(z-(coreZ+117))<=4&&(x<coreX||x>coreX+234)));
                // Keep the apron flush with the four original gate ramps.
                int cap=gate?base:boundingBox.maxY();
                for(int y=cap;y>=Math.max(world.getMinBuildHeight()+1,boundingBox.minY());y--) {
                    at.set(x,y,z);var old=world.getBlockState(at);
                    if(!old.is(BlockTags.LEAVES) && !old.is(BlockTags.LOGS) && old.isCollisionShapeFullBlock(world,at))break;
                    if(chunk.isInside(at))world.setBlock(at,stone,2);
                }
            }
    }
}

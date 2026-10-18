package com.continuityworks.alfheimcompanion.worldgen;

import com.mojang.serialization.Codec;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.chunk.ChunkGeneratorStructureState;
import net.minecraft.world.level.levelgen.structure.placement.*;

/** Uses the SAME seeded kilometre-ring family as the existing remote districts. */
public final class LabyrinthRingPlacement extends RandomSpreadStructurePlacement {
    public static final Codec<LabyrinthRingPlacement> CODEC=Codec.unit(LabyrinthRingPlacement::new);
    public LabyrinthRingPlacement(){
        super(DistrictRings.CELL_CHUNKS,0,RandomSpreadType.LINEAR,202610183);
    }
    @Override public ChunkPos getPotentialStructureChunk(long seed,int x,int z){
        return LabyrinthSiteAllocation.inCell(seed,x,z)
            .map(s->new ChunkPos(s.chunkX(),s.chunkZ()))
            .orElseGet(()->super.getPotentialStructureChunk(seed,x,z));
    }
    @Override protected boolean isPlacementChunk(ChunkGeneratorStructureState state,int x,int z){
        return LabyrinthSiteAllocation.at(state.getLevelSeed(),x,z).isPresent();
    }
    @Override public StructurePlacementType<?> type(){
        return ModHarborStructures.LABYRINTH_RINGS.get();
    }
}

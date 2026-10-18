package com.continuityworks.alfheimcompanion.worldgen;

import com.mojang.serialization.Codec;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.chunk.ChunkGeneratorStructureState;
import net.minecraft.world.level.levelgen.structure.placement.*;

/** Random-spread locator compatibility; only explicit ring nodes can generate. */
public final class DistrictRingPlacement extends RandomSpreadStructurePlacement {
    public static final Codec<DistrictRingPlacement> CODEC=Codec.unit(DistrictRingPlacement::new);
    public DistrictRingPlacement(){super(DistrictRings.CELL_CHUNKS,0,RandomSpreadType.LINEAR,202610150);}
    @Override public ChunkPos getPotentialStructureChunk(long seed,int x,int z) {
        return DistrictRings.inCell(seed,x,z).map(s->new ChunkPos(s.chunkX(),s.chunkZ()))
            .orElseGet(()->super.getPotentialStructureChunk(seed,x,z));
    }
    @Override protected boolean isPlacementChunk(ChunkGeneratorStructureState state,int x,int z) {
        return DistrictRings.at(state.getLevelSeed(),x,z).isPresent();
    }
    @Override public StructurePlacementType<?> type(){return ModHarborStructures.DISTRICT_RINGS.get();}
}

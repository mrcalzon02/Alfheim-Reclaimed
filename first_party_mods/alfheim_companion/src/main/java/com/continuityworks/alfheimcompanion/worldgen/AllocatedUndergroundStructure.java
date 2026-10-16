package com.continuityworks.alfheimcompanion.worldgen;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureType;
import net.minecraft.world.level.levelgen.structure.structures.JigsawStructure;
import net.minecraft.world.level.levelgen.structure.placement.RandomSpreadStructurePlacement;
import net.minecraft.world.level.levelgen.structure.placement.RandomSpreadType;
import java.util.Optional;

/** Pack-owned layouts yield to sparse upper-rock reservations before any terrain work. */
public final class AllocatedUndergroundStructure extends Structure {
    public static final Codec<AllocatedUndergroundStructure> CODEC=RecordCodecBuilder.create(i->i.group(
        settingsCodec(i),JigsawStructure.CODEC.fieldOf("layout").forGetter(s->s.layout)
    ).apply(i,AllocatedUndergroundStructure::new));
    private static final RandomSpreadStructurePlacement UPPER=new RandomSpreadStructurePlacement(
        UndergroundAllocation.SPACING,UndergroundAllocation.SEPARATION,RandomSpreadType.LINEAR,UndergroundAllocation.SALT);
    private final JigsawStructure layout;
    public AllocatedUndergroundStructure(StructureSettings settings,JigsawStructure layout) {super(settings);this.layout=layout;}
    static boolean reserved(GenerationContext c) {
        int rx=Math.floorDiv(c.chunkPos().x,UndergroundAllocation.SPACING),rz=Math.floorDiv(c.chunkPos().z,UndergroundAllocation.SPACING);
        // A candidate can move at most 31 chunks within its 80-chunk cell.
        // Only adjacent cells can approach within 50 chunks: nine pure hash probes.
        for(int dx=-1;dx<=1;dx++)for(int dz=-1;dz<=1;dz++) {
            var p=UPPER.getPotentialStructureChunk(c.seed(),(rx+dx)*UndergroundAllocation.SPACING,(rz+dz)*UndergroundAllocation.SPACING);
            if(UndergroundAllocation.selected(c.seed(),p.x,p.z)
                && UndergroundAllocation.overlaps(c.chunkPos().x,c.chunkPos().z,p.x,p.z))return true;
        }
        return false;
    }
    @Override protected Optional<GenerationStub> findGenerationPoint(GenerationContext c) {
        if(VoidWarPolicy.reserved(c) || reserved(c))return Optional.empty();
        return layout.findGenerationPoint(c);
    }
    @Override public StructureType<?> type() {return ModHarborStructures.ALLOCATED_UNDERGROUND.get();}
}

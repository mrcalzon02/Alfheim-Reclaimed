package com.continuityworks.alfheimcompanion.worldgen;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureType;
import net.minecraft.world.level.levelgen.structure.structures.JigsawStructure;
import java.util.Optional;

/** Existing pack-owned Void neighbors retain their layout and yield to rare war sites. */
public final class VoidWarNeighborStructure extends Structure {
    public static final Codec<VoidWarNeighborStructure> CODEC=RecordCodecBuilder.create(i->i.group(
        settingsCodec(i),JigsawStructure.CODEC.fieldOf("layout").forGetter(s->s.layout)
    ).apply(i,VoidWarNeighborStructure::new));
    private final JigsawStructure layout;
    public VoidWarNeighborStructure(StructureSettings settings,JigsawStructure layout) {super(settings);this.layout=layout;}
    @Override protected Optional<GenerationStub> findGenerationPoint(GenerationContext c) {
        return VoidWarPolicy.reserved(c)?Optional.empty():layout.findGenerationPoint(c);
    }
    @Override public StructureType<?> type() {return ModHarborStructures.VOID_WAR_NEIGHBOR.get();}
}

package com.continuityworks.alfheimcompanion.worldgen;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.world.level.levelgen.structure.*;
import net.minecraft.world.level.levelgen.structure.structures.JigsawStructure;
import java.util.Optional;

/** Existing small pack works yield to reserved sky villages; layouts remain unchanged. */
public final class FairyReservedJigsawStructure extends Structure {
    public static final Codec<FairyReservedJigsawStructure> CODEC=RecordCodecBuilder.create(i->i.group(
        settingsCodec(i),JigsawStructure.CODEC.fieldOf("layout").forGetter(s->s.layout)
    ).apply(i,FairyReservedJigsawStructure::new));
    private final JigsawStructure layout;
    public FairyReservedJigsawStructure(StructureSettings settings,JigsawStructure layout){super(settings);this.layout=layout;}
    @Override protected Optional<GenerationStub> findGenerationPoint(GenerationContext c){
        return FairyIslandReservations.reserved(c) || WorldstoneCavernStructure.reserved(c)?Optional.empty():layout.findGenerationPoint(c);
    }
    @Override public StructureType<?> type(){return ModHarborStructures.FAIRY_RESERVED.get();}
}

package com.continuityworks.alfheimcompanion.worldgen;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureType;
import net.minecraft.world.level.levelgen.structure.structures.JigsawStructure;
import java.util.Optional;

/** Vanilla jigsaw codec/layout, guarded before any terrain work or piece assembly. */
public final class RemoteDistrictStructure extends Structure {
    public static final Codec<RemoteDistrictStructure> CODEC=RecordCodecBuilder.create(i->i.group(
        settingsCodec(i),JigsawStructure.CODEC.fieldOf("layout").forGetter(s->s.layout)
    ).apply(i,RemoteDistrictStructure::new));
    private final JigsawStructure layout;
    public RemoteDistrictStructure(StructureSettings settings,JigsawStructure layout) {super(settings);this.layout=layout;}
    @Override protected Optional<GenerationStub> findGenerationPoint(GenerationContext c) {
        var id=c.registryAccess().registryOrThrow(Registries.STRUCTURE).getKey(this);
        if(id==null || !DistrictPolicy.allowed(c,id.getPath()))return Optional.empty();
        return layout.findGenerationPoint(c);
    }
    @Override public StructureType<?> type() {return ModHarborStructures.REMOTE_DISTRICT.get();}
}

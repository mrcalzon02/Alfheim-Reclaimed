package com.continuityworks.alfheimcompanion.worldgen;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.*;
import net.minecraft.world.level.levelgen.structure.placement.RandomSpreadStructurePlacement;
import net.minecraft.world.level.levelgen.structure.pools.*;
import java.util.Optional;

/** Four fixed-offset related tiles form one large island; no optional jigsaw children can disappear. */
public final class FeySkyVillageStructure extends Structure {
    public static final Codec<FeySkyVillageStructure> CODEC=RecordCodecBuilder.create(i->i.group(settingsCodec(i),Codec.intRange(0,3).fieldOf("season").forGetter(s->s.season)).apply(i,FeySkyVillageStructure::new));
    private final int season;
    public FeySkyVillageStructure(StructureSettings settings,int season){super(settings);this.season=season;}
    @Override protected Optional<GenerationStub> findGenerationPoint(GenerationContext c){
        int x=c.chunkPos().getMiddleBlockX()-48,z=c.chunkPos().getMiddleBlockZ()-48,y=192;
        if(y+48>c.heightAccessor().getMaxBuildHeight())return Optional.empty();
        // Reject terrain intrusion and biome-edge clipping before adding any pieces.
        for(int dx:new int[]{8,28,48,68,87})for(int dz:new int[]{8,28,48,68,87}){
            if(c.chunkGenerator().getBaseHeight(x+dx,z+dz,Heightmap.Types.WORLD_SURFACE_WG,c.heightAccessor(),c.randomState())>=y-8)return Optional.empty();
            if(!biomes().contains(c.biomeSource().getNoiseBiome((x+dx)>>2,16,(z+dz)>>2,c.randomState().sampler())))return Optional.empty();
        }
        // Independent families reserve a conservative 900-block centre gap:
        // island half-width 48 + the pack's largest 256 half-width + 500 clearance.
        for(var entry:c.registryAccess().registryOrThrow(Registries.STRUCTURE_SET).entrySet()){
            var set=entry.getValue();
            if(set.structures().stream().allMatch(s->s.structure().value() instanceof FeySkyVillageStructure))continue;
            boolean relevant=set.structures().stream().anyMatch(s->s.structure().value().biomes().stream().anyMatch(biomes()::contains));
            if(!relevant)continue;
            if(!(set.placement() instanceof RandomSpreadStructurePlacement placement))return Optional.empty();
            int spacing=placement.spacing(),rx=Math.floorDiv(c.chunkPos().x,spacing),rz=Math.floorDiv(c.chunkPos().z,spacing),reach=(int)Math.ceil(900.0/(spacing*16))+1;
            for(int dx=-reach;dx<=reach;dx++)for(int dz=-reach;dz<=reach;dz++){
                var p=placement.getPotentialStructureChunk(c.seed(),(rx+dx)*spacing,(rz+dz)*spacing);
                if(Math.abs(((long)p.x-c.chunkPos().x)*16)>=900||Math.abs(((long)p.z-c.chunkPos().z)*16)>=900)continue;
                boolean eligible=set.structures().stream().anyMatch(s->s.structure().value().biomes().contains(c.biomeSource().getNoiseBiome(p.getMiddleBlockX()>>2,16,p.getMiddleBlockZ()>>2,c.randomState().sampler())));
                if(eligible)return Optional.empty();
            }
        }
        int layout=c.random().nextInt(2);
        String name=com.continuityworks.alfheimcompanion.fey.ModFeyHomes.SEASONS[season];
        return Optional.of(new GenerationStub(new BlockPos(x+48,y+14,z+48),builder->{
            for(int gz=0;gz<2;gz++)for(int gx=0;gx<2;gx++){
                var pos=new BlockPos(x+gx*48,y,z+gz*48);
                var element=StructurePoolElement.single("alfheim:pixie/"+name+"/village_"+layout+"_"+gx+"_"+gz).apply(StructureTemplatePool.Projection.RIGID);
                builder.addPiece(new PoolElementStructurePiece(c.structureTemplateManager(),element,pos,1,Rotation.NONE,element.getBoundingBox(c.structureTemplateManager(),pos,Rotation.NONE)));
            }
        }));
    }
    @Override public StructureType<?> type(){return ModHarborStructures.FEY_SKY_VILLAGE.get();}
}

package com.continuityworks.alfheimcompanion.worldgen;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.*;
import net.minecraft.world.level.levelgen.structure.placement.RandomSpreadStructurePlacement;
import net.minecraft.world.level.levelgen.structure.placement.ConcentricRingsStructurePlacement;
import net.minecraftforge.server.ServerLifecycleHooks;
import net.minecraft.world.level.levelgen.structure.pools.*;
import java.util.Optional;

/** Four fixed-offset related tiles form one large island; no optional jigsaw children can disappear. */
public final class FeySkyVillageStructure extends Structure {
    public static final Codec<FeySkyVillageStructure> CODEC=RecordCodecBuilder.create(i->i.group(settingsCodec(i),Codec.intRange(0,3).fieldOf("season").forGetter(s->s.season)).apply(i,FeySkyVillageStructure::new));
    private final int season;
    public FeySkyVillageStructure(StructureSettings settings,int season){super(settings);this.season=season;}
    String siteRejection(GenerationContext c){
        int x=c.chunkPos().getMiddleBlockX()-48,z=c.chunkPos().getMiddleBlockZ()-48,y=192;
        if(y+48>c.heightAccessor().getMaxBuildHeight())return "height";
        long anchorX=x+48,anchorZ=z+48;
        if(anchorX*anchorX+anchorZ*anchorZ<900L*900)return "hub";
        if(!biomes().contains(c.biomeSource().getNoiseBiome((x+48)>>2,16,(z+48)>>2,c.randomState().sampler())))return "anchor_biome";
        var voids=net.minecraft.tags.TagKey.create(Registries.BIOME,new net.minecraft.resources.ResourceLocation("alfheim","void_margins"));
        // A floating island keeps its anchor's season above ordinary biome boundaries.
        // Its complete envelope must still avoid high terrain and the Void margin.
        for(int dx:new int[]{8,28,48,68,87})for(int dz:new int[]{8,28,48,68,87}){
            if(c.chunkGenerator().getBaseHeight(x+dx,z+dz,Heightmap.Types.WORLD_SURFACE_WG,c.heightAccessor(),c.randomState())>=y-8)return "terrain";
            if(c.biomeSource().getNoiseBiome((x+dx)>>2,16,(z+dz)>>2,c.randomState().sampler()).is(voids))return "void_edge";
        }
        return "none";
    }
    String rejection(GenerationContext c){
        String site=siteRejection(c);if(!site.equals("none"))return site;
        // Independent families reserve a conservative 900-block centre gap:
        // island half-width 48 + the pack's largest 256 half-width + 500 clearance.
        var server=ServerLifecycleHooks.getCurrentServer();
        var home=server==null?null:server.getLevel(net.minecraft.resources.ResourceKey.create(Registries.DIMENSION,new net.minecraft.resources.ResourceLocation("mythicbotany","alfheim")));
        if(home==null)return "world_unavailable";
        var state=home.getChunkSource().getGeneratorState();
        var own=c.registryAccess().registryOrThrow(Registries.STRUCTURE_SET).get(new net.minecraft.resources.ResourceLocation("alfheim","pixie_spring_hamlet"));
        boolean onGrid=own!=null && own.placement().isStructureChunk(state,c.chunkPos().x,c.chunkPos().z);
        for(var entry:c.registryAccess().registryOrThrow(Registries.STRUCTURE_SET).entrySet()){
            var set=entry.getValue();
            if(set.structures().stream().allMatch(s->s.structure().value() instanceof FeySkyVillageStructure))continue;
            // These adapters enforce the inverse reservation against this same valid
            // shared-grid candidate. Rechecking their terrain cannot change it.
            if(onGrid && set.structures().stream().allMatch(s->s.structure().value() instanceof AllocatedUndergroundStructure
                || s.structure().value() instanceof UpperUnderworldStructure
                || s.structure().value() instanceof FairyReservedJigsawStructure
                || s.structure().value() instanceof VoidWarNeighborStructure
                || s.structure().value() instanceof WorldstoneCavernStructure
                || s.structure().value() instanceof VoidSurfaceStructure))continue;
            boolean relevant=set.structures().stream().anyMatch(s->s.structure().value().biomes().stream().anyMatch(c.biomeSource().possibleBiomes()::contains));
            if(!relevant)continue;
            if(set.placement() instanceof ConcentricRingsStructurePlacement rings){
                var positions=state.getRingPositionsFor(rings);
                if(positions!=null)for(var p:positions)
                    if(Math.abs(((long)p.x-c.chunkPos().x)*16)<900 && Math.abs(((long)p.z-c.chunkPos().z)*16)<900)return "neighbor:"+entry.getKey().location();
                continue;
            }
            if(!(set.placement() instanceof RandomSpreadStructurePlacement placement))return "unsupported:"+entry.getKey().location();
            int spacing=placement.spacing(),rx=Math.floorDiv(c.chunkPos().x,spacing),rz=Math.floorDiv(c.chunkPos().z,spacing),reach=(int)Math.ceil(900.0/(spacing*16))+1;
            for(int dx=-reach;dx<=reach;dx++)for(int dz=-reach;dz<=reach;dz++){
                var p=placement.getPotentialStructureChunk(c.seed(),(rx+dx)*spacing,(rz+dz)*spacing);
                if(!placement.isStructureChunk(state,p.x,p.z))continue;
                if(Math.abs(((long)p.x-c.chunkPos().x)*16)>=900||Math.abs(((long)p.z-c.chunkPos().z)*16)>=900)continue;
                String family=entry.getKey().location().getPath();
                if(entry.getKey().location().getNamespace().equals("alfheim") && DistrictPolicy.FAMILIES.contains(family)
                    && DistrictPolicy.winner(c.seed(),p.x,p.z)!=DistrictPolicy.FAMILIES.indexOf(family))continue;
                boolean eligible=false;
                for(var selected:set.structures()) {
                    var structure=selected.structure().value();
                    if(!structure.biomes().contains(c.biomeSource().getNoiseBiome(p.getMiddleBlockX()>>2,16,p.getMiddleBlockZ()>>2,c.randomState().sampler())))continue;
                    var other=new GenerationContext(c.registryAccess(),c.chunkGenerator(),c.biomeSource(),c.randomState(),c.structureTemplateManager(),c.seed(),p,c.heightAccessor(),structure.biomes()::contains);
                    if(structure.findValidGenerationPoint(other).isPresent()){eligible=true;break;}
                }
                if(eligible)return "neighbor:"+entry.getKey().location();
            }
        }
        return "none";
    }
    @Override protected Optional<GenerationStub> findGenerationPoint(GenerationContext c){
        if(!rejection(c).equals("none"))return Optional.empty();
        int x=c.chunkPos().getMiddleBlockX()-48,z=c.chunkPos().getMiddleBlockZ()-48,y=192;
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

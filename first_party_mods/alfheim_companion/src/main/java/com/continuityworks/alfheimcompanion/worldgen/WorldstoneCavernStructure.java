package com.continuityworks.alfheimcompanion.worldgen;

import com.mojang.serialization.Codec;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.RandomState;
import net.minecraft.world.level.levelgen.structure.*;
import net.minecraft.world.level.levelgen.structure.placement.*;
import net.minecraftforge.server.ServerLifecycleHooks;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/** One rare, fully underground mountain chamber. Noise density itself is never modified. */
public final class WorldstoneCavernStructure extends Structure {
    public static final Codec<WorldstoneCavernStructure> CODEC=simpleCodec(WorldstoneCavernStructure::new);
    public static final ResourceLocation ID=new ResourceLocation("alfheim","mountain_worldstone");
    private static final Map<RandomState,ConcurrentHashMap<Long,Probe>> CACHE=Collections.synchronizedMap(new WeakHashMap<>());
    public record Probe(String reason,int summit,int minimumCover) {}
    public WorldstoneCavernStructure(StructureSettings settings){super(settings);}
    Probe site(GenerationContext c) {
        ConcurrentHashMap<Long,Probe> values;
        synchronized(CACHE){values=CACHE.computeIfAbsent(c.randomState(),s->new ConcurrentHashMap<>());}
        if(values.size()>8192)values.clear();
        return values.computeIfAbsent(c.chunkPos().toLong(),key->terrain(c));
    }
    private Probe terrain(GenerationContext c) {
        int x=c.chunkPos().getMiddleBlockX(),z=c.chunkPos().getMiddleBlockZ();
        if((long)x*x+(long)z*z<6000L*6000)return new Probe("hub_castle",0,0);
        if(!biomes().contains(c.biomeSource().getNoiseBiome(x>>2,16,z>>2,c.randomState().sampler())))return new Probe("biome",0,0);
        int summit=c.chunkGenerator().getBaseHeight(x,z,Heightmap.Types.OCEAN_FLOOR_WG,c.heightAccessor(),c.randomState());
        if(summit<WorldstoneLayout.MIN_SUMMIT)return new Probe("low_mountain",summit,0);
        int minimum=Integer.MAX_VALUE;
        var voids=net.minecraft.tags.TagKey.create(Registries.BIOME,new ResourceLocation("alfheim","void_margins"));
        for(int dx=-112;dx<=112;dx+=28)for(int dz=-112;dz<=112;dz+=28) {
            double radial=dx*dx/(114.0*114)+dz*dz/(110.0*110);
            if(radial>1.065)continue;
            if(c.biomeSource().getNoiseBiome((x+dx)>>2,16,(z+dz)>>2,c.randomState().sampler()).is(voids))return new Probe("void_edge",summit,0);
            int roof=(int)Math.ceil(60+100*Math.sqrt(Math.max(0,1.065-radial))+4);
            int surface=c.chunkGenerator().getBaseHeight(x+dx,z+dz,Heightmap.Types.OCEAN_FLOOR_WG,c.heightAccessor(),c.randomState());
            minimum=Math.min(minimum,surface-roof);
            if(minimum<WorldstoneLayout.ROOF)return new Probe("mountain_cover",summit,minimum);
        }
        return new Probe("none",summit,minimum);
    }
    /** Primitive inverse reservation only: no recursive neighbor generation or chunk loads. */
    static boolean reserved(GenerationContext c) {
        var set=c.registryAccess().registryOrThrow(Registries.STRUCTURE_SET).get(ID);
        var value=c.registryAccess().registryOrThrow(Registries.STRUCTURE).get(ID);
        if(!(value instanceof WorldstoneCavernStructure stone) || set==null
            || !(set.placement() instanceof RandomSpreadStructurePlacement placement))return false;
        int rx=Math.floorDiv(c.chunkPos().x,placement.spacing()),rz=Math.floorDiv(c.chunkPos().z,placement.spacing());
        for(int dx=-1;dx<=1;dx++)for(int dz=-1;dz<=1;dz++) {
            var p=placement.getPotentialStructureChunk(c.seed(),(rx+dx)*placement.spacing(),(rz+dz)*placement.spacing());
            if(Math.abs(((long)p.x-c.chunkPos().x)*16)>=WorldstoneLayout.CLEARANCE
                || Math.abs(((long)p.z-c.chunkPos().z)*16)>=WorldstoneLayout.CLEARANCE)continue;
            var other=new GenerationContext(c.registryAccess(),c.chunkGenerator(),c.biomeSource(),c.randomState(),
                c.structureTemplateManager(),c.seed(),p,c.heightAccessor(),stone.biomes()::contains);
            if(stone.site(other).reason().equals("none"))return true;
        }
        return false;
    }
    static boolean yields(Structure s) {
        return s instanceof FairyReservedJigsawStructure || s instanceof AllocatedUndergroundStructure
            || s instanceof UpperUnderworldStructure || s instanceof VoidWarNeighborStructure || s instanceof VoidSurfaceStructure;
    }
    String rejection(GenerationContext c) {
        String reason=site(c).reason();if(!reason.equals("none"))return reason;
        if(FairyIslandReservations.reserved(c))return "fairy_island";
        var server=ServerLifecycleHooks.getCurrentServer();
        var home=server==null?null:server.getLevel(net.minecraft.resources.ResourceKey.create(Registries.DIMENSION,new ResourceLocation("mythicbotany","alfheim")));
        if(home==null)return "world_unavailable";
        var state=home.getChunkSource().getGeneratorState();var sets=c.registryAccess().registryOrThrow(Registries.STRUCTURE_SET);
        var own=sets.get(ID);boolean onGrid=own!=null && own.placement().isStructureChunk(state,c.chunkPos().x,c.chunkPos().z);
        for(var entry:sets.entrySet()) {
            var set=entry.getValue();
            if(entry.getKey().location().equals(ID))continue;
            if(onGrid && set.structures().stream().allMatch(s->yields(s.structure().value())))continue;
            if(!set.structures().stream().anyMatch(s->s.structure().value().biomes().stream().anyMatch(c.biomeSource().possibleBiomes()::contains)))continue;
            if(set.placement() instanceof ConcentricRingsStructurePlacement rings) {
                var positions=state.getRingPositionsFor(rings);
                if(positions!=null)for(var p:positions)
                    if(near(c.chunkPos(),p))return "neighbor:"+entry.getKey().location();
                continue;
            }
            if(!(set.placement() instanceof RandomSpreadStructurePlacement placement))return "unsupported:"+entry.getKey().location();
            int spacing=placement.spacing(),rx=Math.floorDiv(c.chunkPos().x,spacing),rz=Math.floorDiv(c.chunkPos().z,spacing);
            int reach=(int)Math.ceil(WorldstoneLayout.CLEARANCE/(spacing*16.0))+1;
            for(int dx=-reach;dx<=reach;dx++)for(int dz=-reach;dz<=reach;dz++) {
                var p=placement.getPotentialStructureChunk(c.seed(),(rx+dx)*spacing,(rz+dz)*spacing);
                if(!near(c.chunkPos(),p) || !placement.isStructureChunk(state,p.x,p.z))continue;
                var key=entry.getKey().location();String family=key.getPath();
                if(key.getNamespace().equals("alfheim") && DistrictPolicy.FAMILIES.contains(family)
                    && DistrictPolicy.winner(c.seed(),p.x,p.z)!=DistrictPolicy.FAMILIES.indexOf(family))continue;
                for(var selected:set.structures()) {
                    var structure=selected.structure().value();
                    if(!structure.biomes().contains(c.biomeSource().getNoiseBiome(p.getMiddleBlockX()>>2,16,p.getMiddleBlockZ()>>2,c.randomState().sampler())))continue;
                    var other=new GenerationContext(c.registryAccess(),c.chunkGenerator(),c.biomeSource(),c.randomState(),
                        c.structureTemplateManager(),c.seed(),p,c.heightAccessor(),structure.biomes()::contains);
                    if(structure.findValidGenerationPoint(other).isPresent())return "neighbor:"+key;
                }
            }
        }
        return "none";
    }
    private static boolean near(ChunkPos a,ChunkPos b) {
        return Math.abs(((long)a.x-b.x)*16)<WorldstoneLayout.CLEARANCE && Math.abs(((long)a.z-b.z)*16)<WorldstoneLayout.CLEARANCE;
    }
    @Override protected Optional<GenerationStub> findGenerationPoint(GenerationContext c) {
        if(!rejection(c).equals("none"))return Optional.empty();
        var centre=new BlockPos(c.chunkPos().getMiddleBlockX(),60,c.chunkPos().getMiddleBlockZ());
        return Optional.of(new GenerationStub(centre,builder->builder.addPiece(new WorldstoneCavernPiece(centre.getX(),centre.getZ()))));
    }
    @Override public StructureType<?> type(){return ModHarborStructures.WORLDSTONE.get();}
}

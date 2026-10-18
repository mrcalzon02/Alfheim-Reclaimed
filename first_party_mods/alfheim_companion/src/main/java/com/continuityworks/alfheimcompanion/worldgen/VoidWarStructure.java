package com.continuityworks.alfheimcompanion.worldgen;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureType;
import net.minecraft.world.level.levelgen.structure.PoolElementStructurePiece;
import net.minecraft.world.level.levelgen.structure.placement.RandomSpreadStructurePlacement;
import net.minecraft.world.level.levelgen.structure.pools.StructurePoolElement;
import net.minecraft.world.level.levelgen.structure.pools.StructureTemplatePool;
import java.util.Optional;

/** One coherent 18-piece war site; strict Void hosts and bounded 25-column fitting. */
public final class VoidWarStructure extends Structure {
    public static final Codec<VoidWarStructure> CODEC=RecordCodecBuilder.create(i->i.group(
        settingsCodec(i),Codec.intRange(0,7).fieldOf("kind").forGetter(s->s.kind)
    ).apply(i,VoidWarStructure::new));
    private final int kind;
    public VoidWarStructure(StructureSettings settings,int kind) {super(settings);this.kind=kind;}
    record Probe(String reason,int x,int y,int z,int columns,int biomeQueries) {boolean accepted(){return reason.equals("accepted");}}
    static Probe probe(GenerationContext c,int kind) {
        int width=kind>=6?47:141,half=(width-1)/2;
        int x=c.chunkPos().getMiddleBlockX()-half,z=c.chunkPos().getMiddleBlockZ()-half,columns=0,queries=1;
        if(!VoidWarPolicy.eligible(c,c.chunkPos()))return new Probe("biome_or_origin",x,0,z,0,queries);
        if(kind!=VoidWarPolicy.winner(c))return new Probe("family_selection",x,0,z,0,queries);
        if(!WorldSiteAllocation.clearProtected(c,c.chunkPos().getMiddleBlockX(),
                c.chunkPos().getMiddleBlockZ(),half,WorldSiteAllocation.GAP))
            return new Probe("protected_site",x,0,z,0,queries);
        if(!WorldSiteAllocation.clearDistricts(c.seed(),c.chunkPos().getMiddleBlockX(),
                c.chunkPos().getMiddleBlockZ(),half,WorldSiteAllocation.GAP))
            return new Probe("district_ring",x,0,z,0,queries);
        // Cooperating legacy Void families and dungeons yield to this grid. Other
        // Void-eligible independent sets keep a conservative reservation.
        var target=c.registryAccess().registryOrThrow(Registries.BIOME).getTagOrEmpty(VoidWarPolicy.BIOMES);
        for(var entry:c.registryAccess().registryOrThrow(Registries.STRUCTURE_SET).entrySet()) {
            var set=entry.getValue();
            boolean relevant=set.structures().stream().anyMatch(s->s.structure().value().biomes().stream().anyMatch(b->{
                for(var allowed:target)if(allowed.equals(b))return true;return false;}));
            if(!relevant || set.structures().stream().allMatch(s->s.structure().value() instanceof VoidWarStructure
                || s.structure().value() instanceof VoidWarNeighborStructure || s.structure().value() instanceof AllocatedUndergroundStructure))continue;
            if(!(set.placement() instanceof RandomSpreadStructurePlacement placement))return new Probe("unsupported_neighbor",x,0,z,0,queries);
            int spacing=placement.spacing(),rx=Math.floorDiv(c.chunkPos().x,spacing),rz=Math.floorDiv(c.chunkPos().z,spacing);
            int reach=(int)Math.ceil(900.0/(spacing*16))+1;
            for(int dx=-reach;dx<=reach;dx++)for(int dz=-reach;dz<=reach;dz++) {
                var p=placement.getPotentialStructureChunk(c.seed(),(rx+dx)*spacing,(rz+dz)*spacing);
                if(Math.abs(((long)p.x-c.chunkPos().x)*16)<900 && Math.abs(((long)p.z-c.chunkPos().z)*16)<900)
                    return new Probe("neighbor:"+entry.getKey().location(),x,0,z,0,queries);
            }
        }
        int[] heights=new int[25];net.minecraft.world.level.NoiseColumn[] host=new net.minecraft.world.level.NoiseColumn[25];int i=0;
        for(int ix=0;ix<5;ix++)for(int iz=0;iz<5;iz++) {
            int dx=ix*(width-1)/4,dz=iz*(width-1)/4;
            heights[i]=c.chunkGenerator().getBaseHeight(x+dx,z+dz,Heightmap.Types.OCEAN_FLOOR_WG,c.heightAccessor(),c.randomState());
            columns++;
            if(heights[i]<60 || heights[i]>160)return new Probe("altitude",x,0,z,columns,queries);
            host[i]=c.chunkGenerator().getBaseColumn(x+dx,z+dz,c.heightAccessor(),c.randomState());i++;
        }
        int surface=VoidWarHost.surface(heights),base=surface-28;
        if(surface<0)return new Probe("relief",x,0,z,columns,queries);
        for(var column:host) {
            if(!column.getBlock(surface).getFluidState().isEmpty())return new Probe("flooded_surface",x,0,z,columns,queries);
            boolean floor=true,roof=true;int solid=0;
            for(int y=base;y<surface;y++) {
                var b=column.getBlock(y);boolean ok=b.canOcclude() && b.getFluidState().isEmpty();
                if(ok)solid++;if(y<=base+4)floor&=ok;if(y>=surface-8 && y<=surface-4)roof&=ok;
            }
            if(!VoidWarHost.solidFrame(floor,roof,solid))return new Probe("host_volume",x,0,z,columns,queries);
        }
        // Every noise-biome cell under the entire footprint, at both occupied
        // strata. No clipping a dungeon into a neighboring land biome.
        for(int qx=x>>2;qx<=(x+width-1)>>2;qx++)for(int qz=z>>2;qz<=(z+width-1)>>2;qz++)
            for(int y:new int[]{base+5,surface+5}) {
                queries++;
                if(!c.biomeSource().getNoiseBiome(qx,y>>2,qz,c.randomState().sampler()).is(VoidWarPolicy.BIOMES))
                    return new Probe("biome_boundary",x,0,z,columns,queries);
            }
        return new Probe("accepted",x,surface,z,columns,queries);
    }
    @Override protected Optional<GenerationStub> findGenerationPoint(GenerationContext c) {
        var site=probe(c,kind);if(!site.accepted())return Optional.empty();
        int grid=kind>=6?1:3,half=(grid*47-1)/2;
        return Optional.of(new GenerationStub(new BlockPos(site.x()+half,site.y(),site.z()+half),builder->{
            // Surface first: the stair piece restores its exact shared opening and landing.
            for(int layer=0;layer<2;layer++)for(int gz=0;gz<grid;gz++)for(int gx=0;gx<grid;gx++) {
                String name=(layer==0?VoidWarLayout.SURFACE:VoidWarLayout.UNDERGROUND)[kind][gz*grid+gx];
                var pos=new BlockPos(site.x()+gx*47,site.y()-(layer==0?4:28),site.z()+gz*47);
                var element=StructurePoolElement.single("alfheim:void_war/"+name).apply(StructureTemplatePool.Projection.RIGID);
                builder.addPiece(new PoolElementStructurePiece(c.structureTemplateManager(),element,pos,1,Rotation.NONE,
                    element.getBoundingBox(c.structureTemplateManager(),pos,Rotation.NONE)));
            }
        }));
    }
    @Override public StructureType<?> type(){return ModHarborStructures.VOID_WAR.get();}
}

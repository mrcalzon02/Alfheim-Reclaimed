package com.continuityworks.alfheimcompanion.worldgen;

import com.mojang.serialization.Codec;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.FluidTags;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureType;
import net.minecraft.world.level.levelgen.structure.PoolElementStructurePiece;
import net.minecraft.world.level.levelgen.structure.pools.StructurePoolElement;
import net.minecraft.world.level.levelgen.structure.pools.StructureTemplatePool;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePiecesBuilder;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructureTemplateManager;
import java.util.HashMap;
import java.util.Optional;
import java.util.function.Consumer;

public final class HarborStructure extends Structure {
    public static final Codec<HarborStructure> CODEC=simpleCodec(HarborStructure::new);
    public HarborStructure(StructureSettings settings) { super(settings); }

    @Override protected Optional<GenerationStub> findGenerationPoint(GenerationContext c) {
        int sea=c.chunkGenerator().getSeaLevel();
        var site=auditGeneratedBounded(c.chunkGenerator(),c.randomState(),c.heightAccessor(),c.chunkPos().getMinBlockX(),c.chunkPos().getMinBlockZ(),false,HarborGeometry.PARTS).site();
        return site.map(s->new GenerationStub(new BlockPos(s.x(),sea+2,s.z()),builder->
            pieces(c.structureTemplateManager(),s,builder::addPiece)));
    }

    public record GeneratedAudit(Optional<HarborSite.Site> site,int columns,boolean parity,String profile,String attempts) {}
    public static GeneratedAudit auditGenerated(net.minecraft.world.level.chunk.ChunkGenerator generator,
            net.minecraft.world.level.levelgen.RandomState random,net.minecraft.world.level.LevelHeightAccessor height,
            int x,int z,boolean verify) {
        return auditGenerated(generator,random,height,x,z,verify,HarborGeometry.PARTS);
    }
    public static GeneratedAudit auditGenerated(net.minecraft.world.level.chunk.ChunkGenerator generator,
            net.minecraft.world.level.levelgen.RandomState random,net.minecraft.world.level.LevelHeightAccessor height,
            int x,int z,boolean verify,HarborGeometry.Part[] parts) {
        return auditGenerated(generator,random,height,x,z,verify,parts,false);
    }
    public static GeneratedAudit auditGeneratedBounded(net.minecraft.world.level.chunk.ChunkGenerator generator,
            net.minecraft.world.level.levelgen.RandomState random,net.minecraft.world.level.LevelHeightAccessor height,
            int x,int z,boolean verify,HarborGeometry.Part[] parts) {
        return auditGenerated(generator,random,height,x,z,verify,parts,true);
    }
    private static GeneratedAudit auditGenerated(net.minecraft.world.level.chunk.ChunkGenerator generator,
            net.minecraft.world.level.levelgen.RandomState random,net.minecraft.world.level.LevelHeightAccessor height,
            int x,int z,boolean verify,HarborGeometry.Part[] parts,boolean bounded) {
        int sea=generator.getSeaLevel();
        var cache=new HashMap<Long,HarborSite.Column>();
        HarborSite.Sampler sampler=(px,pz)->cache.computeIfAbsent(BlockPos.asLong(px,0,pz),key->{
            var column=generator.getBaseColumn(px,pz,height,random);
            int surface=height.getMinBuildHeight(),floor=height.getMinBuildHeight();
            boolean foundSurface=false,foundFloor=false;
            for(int y=height.getMaxBuildHeight()-1;y>=height.getMinBuildHeight();y--) {
                var block=column.getBlock(y);
                if(!foundSurface && Heightmap.Types.WORLD_SURFACE_WG.isOpaque().test(block)) {surface=y+1;foundSurface=true;}
                if(!foundFloor && Heightmap.Types.OCEAN_FLOOR_WG.isOpaque().test(block)) {floor=y+1;foundFloor=true;}
                if(foundSurface && foundFloor) break;
            }
            return new HarborSite.Column(surface,floor,column.getBlock(sea-1).getFluidState().is(FluidTags.WATER));
        });
        var attempts=new java.util.StringJoiner(";");
        Optional<HarborSite.Site> site;
        if(bounded) {
            var result=HarborSite.findBounded(x,z,sea,sampler,parts,System::nanoTime,
                HarborSite.GENERATION_COLUMN_LIMIT,HarborSite.GENERATION_TIME_LIMIT);
            site=result.site();attempts.add("bounded:"+result.outcome());
        } else site=HarborSite.find(x,z,sea,sampler,parts,verify?a->{
            var c=a.lastColumn();
            attempts.add(a.rotation()+","+a.lift()+","+a.requests()+","+a.lastX()+","+a.lastZ()+":"+
                (c==null?"missing":c.surface()+","+c.floor()+","+c.water())+","+a.accepted());
        }:null);
        boolean parity=true;
        if(verify) {
            int checked=0;
            for(var entry:cache.entrySet()) {
                BlockPos at=BlockPos.of(entry.getKey());var value=entry.getValue();
                parity &= value.surface()==generator.getBaseHeight(at.getX(),at.getZ(),Heightmap.Types.WORLD_SURFACE_WG,height,random)
                       && value.floor()==generator.getBaseHeight(at.getX(),at.getZ(),Heightmap.Types.OCEAN_FLOOR_WG,height,random);
                if(++checked==(bounded?2:8)) break;
            }
        }
        var profile=new java.util.StringJoiner(";");
        if(verify) cache.entrySet().stream().sorted(java.util.Map.Entry.comparingByKey()).limit(16).forEach(e->{
            var at=BlockPos.of(e.getKey());var v=e.getValue();
            profile.add(at.getX()+","+at.getZ()+":"+v.surface()+","+v.floor()+","+v.water());
        });
        return new GeneratedAudit(site,cache.size(),parity,profile.toString(),attempts.toString());
    }

    public static void pieces(StructureTemplateManager manager,HarborSite.Site site,Consumer<PoolElementStructurePiece> accept) {
        for (HarborGeometry.Part part:HarborGeometry.PARTS) {
            int[] offset=HarborGeometry.rotate(part.x(),part.z(),site.rotation());
            BlockPos position=new BlockPos(site.x()+offset[0],site.baseY(),site.z()+offset[1]);
            Rotation rotation=Rotation.values()[(part.rotation()+site.rotation())%4];
            var element=StructurePoolElement.single("alfheim:ancient/harbor_complex/"+part.name()).apply(StructureTemplatePool.Projection.RIGID);
            if(site.quayLift()>0) {
                int a=part.maxX()-part.minX()+1,b=part.maxZ()-part.minZ()+1;
                int width=part.rotation()%2==0?a:b,depth=part.rotation()%2==0?b:a;
                var footer=StructurePoolElement.single("alfheim:ancient/harbor_complex/foundations/"+width+"x"+depth+"_"+site.quayLift()).apply(StructureTemplatePool.Projection.RIGID);
                var bottom=position.below(site.quayLift());
                accept.accept(new PoolElementStructurePiece(manager,footer,bottom,1,rotation,footer.getBoundingBox(manager,bottom,rotation)));
            }
            accept.accept(new PoolElementStructurePiece(manager,element,position,1,rotation,element.getBoundingBox(manager,position,rotation)));
        }
    }
    @Override public StructureType<?> type() { return ModHarborStructures.HARBOR.get(); }
}

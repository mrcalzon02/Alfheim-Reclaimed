package com.continuityworks.alfheimcompanion.worldgen;

import com.mojang.serialization.Codec;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureType;
import java.util.Optional;

/** A single reserved start owns monastery, six vendor stalls, 54 rooms and every connector. */
public final class MonasteryLabyrinthStructure extends Structure {
    public static final Codec<MonasteryLabyrinthStructure> CODEC=
        simpleCodec(MonasteryLabyrinthStructure::new);
    private static final int[] XS={-64,-32,0,32,64,96},ZS={-32,0,32};
    public MonasteryLabyrinthStructure(StructureSettings settings){super(settings);}

    @Override protected Optional<GenerationStub> findGenerationPoint(GenerationContext c){
        var possible=LabyrinthSiteAllocation.at(c.seed(),c.chunkPos().x,c.chunkPos().z);
        if(possible.isEmpty())return Optional.empty();
        var site=possible.get();
        if(site.act()<1 || !LabyrinthSiteAllocation.clearsDistricts(c.seed(),site)
            || !WorldSiteAllocation.clearProtected(c,site.x(),site.z(),
                LabyrinthSiteAllocation.HALF_WIDTH,WorldSiteAllocation.GAP))
            return Optional.empty();
        int x=site.x(),z=site.z(),sea=c.chunkGenerator().getSeaLevel();
        int surface=c.chunkGenerator().getBaseHeight(x,z,
            Heightmap.Types.OCEAN_FLOOR_WG,c.heightAccessor(),c.randomState());
        if(surface<sea+1 || surface>sea+28
            || surface+26>=c.heightAccessor().getMaxBuildHeight())return Optional.empty();
        // The monastery AND village must rest on competent surface terrain.
        // 18 bounded noise-column probes, no chunk loads, no rescue islands.
        for(int dx:XS)for(int dz:ZS){
            int px=x+dx,pz=z+dz;
            int y=c.chunkGenerator().getBaseHeight(px,pz,
                Heightmap.Types.OCEAN_FLOOR_WG,c.heightAccessor(),c.randomState());
            if(Math.abs(y-surface)>4||y<=sea)return Optional.empty();
            var column=c.chunkGenerator().getBaseColumn(px,pz,c.heightAccessor(),c.randomState());
            for(int depth=0;depth<=4;depth++){
                var block=column.getBlock(y-depth-1);
                if(block.isAir()||!block.getFluidState().isEmpty())return Optional.empty();
            }
            if(!column.getBlock(y).getFluidState().isEmpty())return Optional.empty();
        }
        int act=site.act(),base=surface;
        long layoutSeed=c.seed()^((long)site.chunkX()<<32)
            ^(site.chunkZ()&0xffffffffL)^0x5A6F1C20261018L;
        var layout=LabyrinthGraphPlan.plan(layoutSeed,act,base,
            c.heightAccessor().getMinBuildHeight());
        return Optional.of(new GenerationStub(new BlockPos(x,base,z),builder->{
            builder.addPiece(new MonasteryLabyrinthPiece("monastery",act,0,0,
                x-32,base-4,z-32,65,29,65));
            builder.addPiece(new MonasteryLabyrinthPiece("village",act,0,0,
                x+36,base-4,z-36,65,22,73));
            builder.addPiece(new MonasteryLabyrinthPiece("approach",act,0,0,
                x+31,base-1,z-3,6,7,7));
            int[] doors=new int[layout.rooms().size()];
            for(var edge:layout.edges()){
                if(edge.connection().equals("vertical_stair"))continue;
                var a=layout.rooms().get(edge.from()),b=layout.rooms().get(edge.to());
                if(a.x()<b.x()){doors[a.id()]|=2;doors[b.id()]|=8;}
                else if(a.x()>b.x()){doors[a.id()]|=8;doors[b.id()]|=2;}
                else if(a.z()<b.z()){doors[a.id()]|=4;doors[b.id()]|=1;}
                else {doors[a.id()]|=1;doors[b.id()]|=4;}
            }
            for(var room:layout.rooms())builder.addPiece(
                new MonasteryLabyrinthPiece("room",act,doors[room.id()],room.id(),
                    x+room.x()-14,room.y(),z+room.z()-14,29,15,29));
            for(var edge:layout.edges()){
                var a=layout.rooms().get(edge.from()),b=layout.rooms().get(edge.to());
                if(edge.connection().equals("vertical_stair")){
                    int low=Math.min(a.y(),b.y()),high=Math.max(a.y(),b.y());
                    builder.addPiece(new MonasteryLabyrinthPiece("shaft",act,0,
                        edge.to(),x+5,low,z+5,7,high-low+8,7));
                }else if(a.x()!=b.x()){
                    int lo=Math.min(a.x(),b.x())+14,hi=Math.max(a.x(),b.x())-14;
                    builder.addPiece(new MonasteryLabyrinthPiece("corridor_x",
                        act,0,edge.to(),x+lo,a.y(),z+a.z()-3,hi-lo+1,8,7));
                }else{
                    int lo=Math.min(a.z(),b.z())+14,hi=Math.max(a.z(),b.z())-14;
                    builder.addPiece(new MonasteryLabyrinthPiece("corridor_z",
                        act,0,edge.to(),x+a.x()-3,a.y(),z+lo,7,8,hi-lo+1));
                }
            }
            int bottom=layout.rooms().get(4).y();
            builder.addPiece(new MonasteryLabyrinthPiece("shaft",act,0,4,
                x+5,bottom,z+5,7,base-bottom+8,7));
        }));
    }
    @Override public StructureType<?> type(){
        return ModHarborStructures.MONASTERY_LABYRINTH.get();
    }
}

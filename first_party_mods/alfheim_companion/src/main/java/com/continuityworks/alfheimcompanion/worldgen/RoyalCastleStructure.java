package com.continuityworks.alfheimcompanion.worldgen;

import com.mojang.serialization.Codec;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.levelgen.structure.placement.ConcentricRingsStructurePlacement;
import net.minecraftforge.server.ServerLifecycleHooks;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureType;
import net.minecraft.world.level.levelgen.structure.PoolElementStructurePiece;
import net.minecraft.world.level.levelgen.structure.pools.StructurePoolElement;
import net.minecraft.world.level.levelgen.structure.pools.StructureTemplatePool;
import java.util.Optional;

/** Three near-origin candidates, only the first suitable site wins; at most 27 columns. */
public final class RoyalCastleStructure extends Structure {
    public static final Codec<RoyalCastleStructure> CODEC=simpleCodec(RoyalCastleStructure::new);
    public RoyalCastleStructure(StructureSettings settings) {super(settings);}
    private int[] probe(GenerationContext c,ChunkPos chunk,boolean natural) {
        int x=chunk.getMinBlockX()-117,z=chunk.getMinBlockZ()-117;
        int low=Integer.MAX_VALUE,high=Integer.MIN_VALUE;
        for(int dx:new int[]{0,117,234})for(int dz:new int[]{0,117,234}) {
            int y=c.chunkGenerator().getBaseHeight(x+dx,z+dz,Heightmap.Types.OCEAN_FLOOR_WG,c.heightAccessor(),c.randomState());
            low=Math.min(low,y);high=Math.max(high,y);
        }
        high=Math.max(high,c.chunkGenerator().getSeaLevel()+1);
        if(low<c.chunkGenerator().getSeaLevel()-48 || high-low>80 || high+48>=c.heightAccessor().getMaxBuildHeight())return null;
        if(natural && !biomes().contains(c.biomeSource().getNoiseBiome((x+117)>>2,high>>2,(z+117)>>2,c.randomState().sampler())))return null;
        return new int[]{x,high,z};
    }
    @Override protected Optional<GenerationStub> findGenerationPoint(GenerationContext c) {
        int[] site=null;
        var server=ServerLifecycleHooks.getCurrentServer();
        var home=server==null?null:server.getLevel(ResourceKey.create(Registries.DIMENSION,new ResourceLocation("mythicbotany","alfheim")));
        var set=c.registryAccess().registryOrThrow(Registries.STRUCTURE_SET).get(new ResourceLocation("alfheim","royal_castle"));
        var ring=home==null || set==null || !(set.placement() instanceof ConcentricRingsStructurePlacement)?null:
            home.getChunkSource().getGeneratorState().getRingPositionsFor((ConcentricRingsStructurePlacement)set.placement());
        if(ring!=null && ring.contains(c.chunkPos())) {
            for(var candidate:ring) {
                var tested=probe(c,candidate,true);
                if(tested==null)continue;
                if(!candidate.equals(c.chunkPos()))return Optional.empty();
                site=tested;break;
            }
        } else site=probe(c,c.chunkPos(),false); // Explicit operator placement outside the ring.
        if(site==null)return Optional.empty();
        final int x=site[0],base=site[1],z=site[2];
            return Optional.of(new GenerationStub(new BlockPos(x+117,base,z+117),builder->{
                builder.addPiece(new RoyalFoundationPiece(x,base,z));
                var manager=c.structureTemplateManager();
                for(int gx=0;gx<5;gx++)for(int gz=0;gz<5;gz++) {
                    String name=(gx==2 && gz==2)?"keep":(gx==0||gx==4)&&(gz==0||gz==4)?"tower":
                        (gx==0||gx==4||gz==0||gz==4)?(gx==2||gz==2?"gate":"curtain"):
                        gx==2||gz==2?"hall":"garden";
                    int r=(gx==4 && gz==0)?1:gz==0?0:gx==4?2-(gz==4?0:1):gz==4?(gx==0?3:2):gx==0?3:0;
                    // Rotate each square about its own centre, preserving the 47-block grid.
                    int px=x+gx*47+(r==1||r==2?46:0),pz=z+gz*47+(r==2||r==3?46:0);
                    var pos=new BlockPos(px,base,pz);var rotation=Rotation.values()[r];
                    var element=StructurePoolElement.single("alfheim:royal_castle/"+name).apply(StructureTemplatePool.Projection.RIGID);
                    builder.addPiece(new PoolElementStructurePiece(manager,element,pos,1,rotation,element.getBoundingBox(manager,pos,rotation)));
                }
            }));
    }
    @Override public StructureType<?> type() {return ModHarborStructures.ROYAL_CASTLE.get();}
}

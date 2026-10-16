package com.continuityworks.alfheimcompanion.worldgen;

import com.mojang.serialization.Codec;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.levelgen.GenerationStep;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureType;
import net.minecraft.world.level.levelgen.structure.structures.JigsawStructure;
import net.minecraft.world.level.levelgen.structure.PoolElementStructurePiece;
import net.minecraft.world.level.levelgen.structure.placement.RandomSpreadStructurePlacement;
import net.minecraft.world.level.levelgen.structure.pools.StructurePoolElement;
import net.minecraft.world.level.levelgen.structure.pools.StructureTemplatePool;
import java.util.Optional;

/** Upper-rock discoveries. Deep density/bedrock are untouched; all authored blocks Y>=32. */
public final class UpperUnderworldStructure extends Structure {
    public static final Codec<UpperUnderworldStructure> CODEC=simpleCodec(UpperUnderworldStructure::new);
    public static final String[] KINDS={"moss_grotto","calcite_drapery","root_vault","buried_cistern",
        "abandoned_gallery","collapsed_archive","silt_pool","basalt_columns","fossil_pocket",
        "crystal_beds","buried_bridge","lithic_fault"};
    public UpperUnderworldStructure(StructureSettings settings) {super(settings);}
    static String reservation(GenerationContext c) {
        int x=c.chunkPos().getMinBlockX(),z=c.chunkPos().getMinBlockZ();
        if((long)x*x+(long)z*z<4000L*4000)return "origin"; // castle + hub reservation
        if(!UndergroundAllocation.selected(c.seed(),c.chunkPos().x,c.chunkPos().z))return "allocation";
        for(var entry:c.registryAccess().registryOrThrow(Registries.STRUCTURE_SET).entrySet()) {
            var key=entry.getKey().location();String id=key.getPath();var set=entry.getValue();
            if(key.toString().equals("alfheim:upper_underworld"))continue;
            // These pack-owned layouts enforce the inverse reservation themselves.
            if(set.structures().stream().allMatch(s->s.structure().value() instanceof AllocatedUndergroundStructure))continue;
            boolean district=key.getNamespace().equals("alfheim") && DistrictPolicy.FAMILIES.contains(id);
            boolean protect=district || set.structures().stream().anyMatch(
                s->s.structure().value().step()==GenerationStep.Decoration.UNDERGROUND_STRUCTURES
                && s.structure().value().biomes().stream().anyMatch(c.biomeSource().possibleBiomes()::contains));
            if(!protect || !(set.placement() instanceof RandomSpreadStructurePlacement placement))continue;
            int spacing=placement.spacing(),rx=Math.floorDiv(c.chunkPos().x,spacing),rz=Math.floorDiv(c.chunkPos().z,spacing);
            int reach=(int)Math.ceil(800.0/(spacing*16))+1;
            for(int dx=-reach;dx<=reach;dx++)for(int dz=-reach;dz<=reach;dz++) {
                var candidate=placement.getPotentialStructureChunk(c.seed(),(rx+dx)*spacing,(rz+dz)*spacing);
                if(Math.abs((long)candidate.getMinBlockX()-x)<800 && Math.abs((long)candidate.getMinBlockZ()-z)<800) {
                    if(set.structures().stream().allMatch(s->s.structure().value() instanceof VoidWarStructure)
                        && !VoidWarPolicy.eligible(c,candidate))continue;
                    // Only the shared-grid winner can actually start a district.
                    if(district && DistrictPolicy.winner(c.seed(),candidate.x,candidate.z)!=DistrictPolicy.FAMILIES.indexOf(id))continue;
                    // Scope eligibility probing to the verified, surface-projected Andwari
                    // definition. Do not probe arbitrary families or assemble any pieces.
                    if(key.toString().equals("mythicbotany:andwari_cave")
                        && set.structures().stream().allMatch(s->s.structure().value() instanceof JigsawStructure)) {
                        boolean viable=false;
                        for(var s:set.structures()) {
                            var structure=s.structure().value();
                            var other=new GenerationContext(c.registryAccess(),c.chunkGenerator(),c.biomeSource(),c.randomState(),
                                c.structureTemplateManager(),c.seed(),candidate,c.heightAccessor(),structure.biomes()::contains);
                            if(structure.findValidGenerationPoint(other).isPresent()) {viable=true;break;}
                        }
                        if(!viable)continue;
                    }
                    return key.toString();
                }
            }
        }
        return "none";
    }
    @Override protected Optional<GenerationStub> findGenerationPoint(GenerationContext c) {
        if(!reservation(c).equals("none"))return Optional.empty();
        int x=c.chunkPos().getMinBlockX()-15,z=c.chunkPos().getMinBlockZ()-15;
        int ceiling=Integer.MAX_VALUE;
        for(int dx:new int[]{0,15,30})for(int dz:new int[]{0,15,30})
            ceiling=Math.min(ceiling,c.chunkGenerator().getBaseHeight(x+dx,z+dz,Heightmap.Types.OCEAN_FLOOR_WG,c.heightAccessor(),c.randomState()));
        int maxY=Math.min(96,ceiling-32);
        if(maxY<32)return Optional.empty();
        int y=32+c.random().nextInt(maxY-31);
        var column=c.chunkGenerator().getBaseColumn(x+15,z+15,c.heightAccessor(),c.randomState());
        if(column.getBlock(y).isAir() || !column.getBlock(y).getFluidState().isEmpty() || column.getBlock(y+19).isAir()
            || !column.getBlock(y+19).getFluidState().isEmpty())return Optional.empty();
        String name=KINDS[c.random().nextInt(KINDS.length)];
        var pos=new BlockPos(x,y,z);
        return Optional.of(new GenerationStub(pos,builder->{
            var element=StructurePoolElement.single("alfheim:upper_underworld/"+name).apply(StructureTemplatePool.Projection.RIGID);
            builder.addPiece(new PoolElementStructurePiece(c.structureTemplateManager(),element,pos,1,Rotation.NONE,
                element.getBoundingBox(c.structureTemplateManager(),pos,Rotation.NONE)));
        }));
    }
    @Override public StructureType<?> type() {return ModHarborStructures.UPPER_UNDERWORLD.get();}
}

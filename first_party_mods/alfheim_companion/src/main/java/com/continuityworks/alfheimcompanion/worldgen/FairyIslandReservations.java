package com.continuityworks.alfheimcompanion.worldgen;

import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.placement.RandomSpreadStructurePlacement;

/** One-way priority over pack-owned small works; no recursive neighbor searches. */
public final class FairyIslandReservations {
    public static boolean reserved(Structure.GenerationContext c) {
        var sets=c.registryAccess().registryOrThrow(Registries.STRUCTURE_SET);
        var set=sets.get(new ResourceLocation("alfheim","pixie_spring_hamlet"));
        if(set==null || !(set.placement() instanceof RandomSpreadStructurePlacement placement))return false;
        int rx=Math.floorDiv(c.chunkPos().x,placement.spacing()),rz=Math.floorDiv(c.chunkPos().z,placement.spacing());
        var structures=c.registryAccess().registryOrThrow(Registries.STRUCTURE);
        for(int dx=-1;dx<=1;dx++)for(int dz=-1;dz<=1;dz++) {
            var p=placement.getPotentialStructureChunk(c.seed(),(rx+dx)*placement.spacing(),(rz+dz)*placement.spacing());
            if(Math.abs(((long)p.x-c.chunkPos().x)*16)>=900 || Math.abs(((long)p.z-c.chunkPos().z)*16)>=900)continue;
            for(String season:new String[]{"spring","summer","autumn","winter"}) {
                if(sets.get(new ResourceLocation("alfheim","pixie_"+season+"_hamlet"))==null)continue;
                var structure=structures.get(new ResourceLocation("alfheim","pixie_"+season+"_hamlet"));
                if(!(structure instanceof FeySkyVillageStructure sky))continue;
                if(!sky.biomes().contains(c.biomeSource().getNoiseBiome(p.getMiddleBlockX()>>2,16,p.getMiddleBlockZ()>>2,c.randomState().sampler())))continue;
                var other=new Structure.GenerationContext(c.registryAccess(),c.chunkGenerator(),c.biomeSource(),c.randomState(),c.structureTemplateManager(),c.seed(),p,c.heightAccessor(),sky.biomes()::contains);
                if(sky.siteRejection(other).equals("none"))return true;
            }
        }
        return false;
    }
    private FairyIslandReservations(){}
}

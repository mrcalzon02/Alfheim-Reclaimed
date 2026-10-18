package com.continuityworks.alfheimcompanion.worldgen;

import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraftforge.server.ServerLifecycleHooks;
import java.util.List;

/** Shared kilometre-ring reservations. No chunk loads or mutable reservations. */
public final class DistrictPolicy {
    public static final int ORIGIN_RADIUS=908, SPAWN_RADIUS=756, CASTLE_CLEARANCE=960;
    public static final List<String> FAMILIES=List.of("common_residential_quarter","elder_lineage_precinct",
        "civic_center","relief_district","scholastic_quarter","production_district",
        "agricultural_estate","roads_trade","harbor_complex","sacred_precinct","military_warden","frontier_stewardship");
    public static int winner(long seed,int chunkX,int chunkZ) {
        return DistrictRings.at(seed,chunkX,chunkZ).map(DistrictRings.Site::family).orElse(-1);
    }
    public static boolean outsideSpawn(int x,int z,int spawnX,int spawnZ) {
        return distanceSquared(x,z,0,0)>=(long)ORIGIN_RADIUS*ORIGIN_RADIUS
            && distanceSquared(x,z,spawnX,spawnZ)>=(long)SPAWN_RADIUS*SPAWN_RADIUS;
    }
    private static long distanceSquared(int x,int z,int a,int b) {long dx=(long)x-a,dz=(long)z-b;return dx*dx+dz*dz;}
    public static boolean allowed(Structure.GenerationContext c,String family) {
        int index=FAMILIES.indexOf(family);
        if(index<0 || winner(c.seed(),c.chunkPos().x,c.chunkPos().z)!=index)return false;
        var server=ServerLifecycleHooks.getCurrentServer();
        if(server==null)return false;
        var home=server.getLevel(ResourceKey.create(Registries.DIMENSION,new ResourceLocation("mythicbotany","alfheim")));
        if(home==null)return false;
        var spawn=home.getSharedSpawnPos();
        int x=c.chunkPos().getMinBlockX(),z=c.chunkPos().getMinBlockZ();
        if(!outsideSpawn(x,z,spawn.getX(),spawn.getZ()))return false;
        // The kilometre-ring winner still owns district placement. Do not revert
        // to the old 192/96 random-spread selection or a 6000-block exclusion.
        var castle=c.registryAccess().registryOrThrow(Registries.STRUCTURE_SET).get(new ResourceLocation("alfheim","royal_castle"));
        if(castle!=null && castle.placement() instanceof net.minecraft.world.level.levelgen.structure.placement.ConcentricRingsStructurePlacement placement) {
            var positions=home.getChunkSource().getGeneratorState().getRingPositionsFor(placement);
            if(positions!=null)for(var p:positions)
                if(distanceSquared(x,z,p.getMinBlockX(),p.getMinBlockZ())<(long)CASTLE_CLEARANCE*CASTLE_CLEARANCE)return false;
        }
        return true;
    }
    private DistrictPolicy() {}
}

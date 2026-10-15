package com.continuityworks.alfheimcompanion.worldgen;

import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraftforge.server.ServerLifecycleHooks;
import java.util.List;

/** Shared deterministic reservation grid. No chunk loads, scans or mutable reservations. */
public final class DistrictPolicy {
    public static final int SPACING=192, SEPARATION=96, ORIGIN_RADIUS=6000, SPAWN_RADIUS=4096;
    public static final List<String> FAMILIES=List.of("common_residential_quarter","elder_lineage_precinct",
        "civic_center","relief_district","scholastic_quarter","production_district",
        "agricultural_estate","roads_trade","harbor_complex","sacred_precinct","military_warden","frontier_stewardship");
    public static int winner(long seed,int chunkX,int chunkZ) {
        long value=seed ^ ((long)Math.floorDiv(chunkX,SPACING)*0x9E3779B97F4A7C15L)
            ^ ((long)Math.floorDiv(chunkZ,SPACING)*0xD1B54A32D192ED03L);
        value=(value^(value>>>30))*0xBF58476D1CE4E5B9L;
        value=(value^(value>>>27))*0x94D049BB133111EBL;
        return (int)Math.floorMod(value^(value>>>31),FAMILIES.size());
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
        return outsideSpawn(c.chunkPos().getMinBlockX(),c.chunkPos().getMinBlockZ(),spawn.getX(),spawn.getZ());
    }
    private DistrictPolicy() {}
}

package com.continuityworks.alfheimcompanion.worldgen;

import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.placement.ConcentricRingsStructurePlacement;
import net.minecraftforge.server.ServerLifecycleHooks;

/** Common, deterministic site envelope policy; never a blanket 4000-block exclusion. */
public final class WorldSiteAllocation {
    public static final int COURT_RADIUS=1024;
    public static final int SPAWN_RADIUS=128;
    public static final int CASTLE_HALF_WIDTH=118;
    public static final int DISTRICT_HALF_WIDTH=256;
    public static final int GAP=128;
    private static final ResourceKey<Level> ALFHEIM=ResourceKey.create(Registries.DIMENSION,
        new ResourceLocation("mythicbotany","alfheim"));

    /** Compare circular central protection to a complete proposed footprint. */
    public static boolean outsideCourt(int x,int z,int footprintRadius,int gap) {
        long clearance=(long)COURT_RADIUS+footprintRadius+gap;
        long dx=x,dz=z;return dx*dx+dz*dz>=clearance*clearance;
    }
    public static boolean outsideMovedSpawn(int x,int z,int sx,int sz,int footprintRadius,int gap) {
        long clearance=(long)SPAWN_RADIUS+footprintRadius+gap;
        long dx=(long)x-sx,dz=(long)z-sz;
        return dx*dx+dz*dz>=clearance*clearance;
    }
    /** Axis-aligned exclusion: both complete footprints plus the specified gap. */
    public static boolean clearEnvelope(int x,int z,int half,int ox,int oz,int otherHalf,int gap) {
        long required=(long)half+otherHalf+gap;
        return Math.abs((long)x-ox)>=required || Math.abs((long)z-oz)>=required;
    }
    /** Theme follows distance from origin, never depth or a sequential act lock. */
    public static int dungeonAct(int x,int z) {
        long radius=(long)x*x+(long)z*z;
        if(radius<1000L*1000)return 0;
        if(radius<2000L*2000)return 1;
        if(radius<3000L*3000)return 2;
        if(radius<4000L*4000)return 3;
        if(radius<5000L*5000)return 4;
        return 5;
    }
    /** Castle uses a concentric-ring set, not the district random-spread grid. */
    public static boolean clearCastle(Structure.GenerationContext c,int x,int z,int half,int gap) {
        var server=ServerLifecycleHooks.getCurrentServer();
        var home=server==null?null:server.getLevel(ALFHEIM);
        if(home==null)return false;
        var set=c.registryAccess().registryOrThrow(Registries.STRUCTURE_SET)
            .get(new ResourceLocation("alfheim","royal_castle"));
        if(set==null || !(set.placement() instanceof ConcentricRingsStructurePlacement placement))
            return false;
        var sites=home.getChunkSource().getGeneratorState().getRingPositionsFor(placement);
        if(sites==null || sites.isEmpty())return false;
        for(var s:sites) {
            // The registered castle is 235x235 around its starting chunk centre.
            if(!clearEnvelope(x,z,half,s.getMinBlockX(),s.getMinBlockZ(),
                              CASTLE_HALF_WIDTH,gap))return false;
        }
        return true;
    }
    /** Shared protection for small archaeology, war sites and the full dungeon family. */
    public static boolean clearProtected(Structure.GenerationContext c,int x,int z,int half,int gap) {
        if(!outsideCourt(x,z,half,gap))return false;
        var server=ServerLifecycleHooks.getCurrentServer();
        var home=server==null?null:server.getLevel(ALFHEIM);
        if(home==null)return false;
        var spawn=home.getSharedSpawnPos();
        return outsideMovedSpawn(x,z,spawn.getX(),spawn.getZ(),half,gap)
            && clearCastle(c,x,z,half,gap);
    }
    /** Reserve the coherent district family site, not 12 independent rolls. */
    public static boolean clearDistricts(long seed,int x,int z,int half,int gap) {
        return !DistrictRings.nearEnvelope(seed,x,z,half+DISTRICT_HALF_WIDTH+gap);
    }
    private WorldSiteAllocation() {}
}

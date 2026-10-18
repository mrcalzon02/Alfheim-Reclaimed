package com.continuityworks.alfheimcompanion.worldgen;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class WorldSiteAllocationTest {
    @Test void actThemeDependsOnlyOnRadialPosition() {
        assertEquals(0,WorldSiteAllocation.dungeonAct(999,0));
        assertEquals(1,WorldSiteAllocation.dungeonAct(1000,0));
        assertEquals(1,WorldSiteAllocation.dungeonAct(-1999,0));
        assertEquals(2,WorldSiteAllocation.dungeonAct(0,2000));
        assertEquals(3,WorldSiteAllocation.dungeonAct(3000,0));
        assertEquals(4,WorldSiteAllocation.dungeonAct(0,-4000));
        assertEquals(5,WorldSiteAllocation.dungeonAct(5000,0));
        assertEquals(5,WorldSiteAllocation.dungeonAct(-6000,0));
    }
    @Test void protectRealFootprintsNotWholeWorld() {
        assertFalse(WorldSiteAllocation.outsideCourt(1000,0,15,128));
        assertTrue(WorldSiteAllocation.outsideCourt(1200,0,15,128));
        assertTrue(WorldSiteAllocation.outsideCourt(3500,0,114,128));
        assertFalse(WorldSiteAllocation.clearEnvelope(0,0,118,500,0,256,128));
        assertTrue(WorldSiteAllocation.clearEnvelope(0,0,118,600,0,256,128));
        assertTrue(WorldSiteAllocation.clearEnvelope(0,0,118,0,600,256,128));
        assertFalse(WorldSiteAllocation.outsideMovedSpawn(1500,0,1500,0,100,128));
        assertTrue(WorldSiteAllocation.outsideMovedSpawn(5000,0,1500,0,100,128));
    }
    @Test void districtSiteProximityUsesCurrentKilometreRingGrid() {
        var site=DistrictRings.site(42,2,1);
        int x=site.chunkX()*16,z=site.chunkZ()*16;
        assertFalse(WorldSiteAllocation.clearDistricts(42,x,z,114,128));
        assertEquals(site, DistrictRings.at(42,site.chunkX(),site.chunkZ()).orElseThrow());
    }
}

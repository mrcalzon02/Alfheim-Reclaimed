package com.continuityworks.alfheimcompanion.worldgen;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class DistrictPolicyTest {
    @Test void protectsHubAndMovedSpawnWithoutExcludingTheInnerRing() {
        assertFalse(DistrictPolicy.outsideSpawn(907,0,0,0));
        assertTrue(DistrictPolicy.outsideSpawn(988,0,80,-112));
        assertFalse(DistrictPolicy.outsideSpawn(12000,0,12000,0));
        assertFalse(DistrictPolicy.outsideSpawn(12755,0,12000,0));
        assertTrue(DistrictPolicy.outsideSpawn(12756,0,12000,0));
        assertTrue(DistrictPolicy.ORIGIN_RADIUS-256-152>=500);
        assertTrue(DistrictPolicy.CASTLE_CLEARANCE-256-167>=500);
    }
    @Test void everyRingAndLocatorCellRecoverTheSameUniqueActiveFamily() {
        boolean[] seen=new boolean[9];
        for(long seed=-25;seed<=25;seed++)for(int ring=1;ring<=100;ring++)for(int slot=0;slot<4;slot++) {
            var site=DistrictRings.site(seed,ring,slot);
            assertEquals(site,DistrictRings.at(seed,site.chunkX(),site.chunkZ()).orElseThrow());
            int rx=Math.floorDiv(site.chunkX(),32)*32,rz=Math.floorDiv(site.chunkZ(),32)*32;
            assertEquals(site,DistrictRings.inCell(seed,rx+31,rz+31).orElseThrow());
            assertEquals(site.family(),DistrictPolicy.winner(seed,site.chunkX(),site.chunkZ()));
            assertTrue(Math.abs(Math.hypot(site.chunkX()*16.0,site.chunkZ()*16.0)-ring*1000)<=12);
            assertTrue(site.family()>=0 && site.family()<9);seen[site.family()]=true;
        }
        for(boolean used:seen)assertTrue(used);
        assertEquals(-1,DistrictPolicy.winner(42,0,0));
    }
    @Test void worstCaseReservationGapExceeds500Blocks() {
        for(long seed=-25;seed<=25;seed++)for(int ring=1;ring<=100;ring++)for(int slot=0;slot<4;slot++) {
            var a=DistrictRings.site(seed,ring,slot);
            for(int otherRing=Math.max(1,ring-2);otherRing<=ring+2;otherRing++)for(int other=0;other<4;other++) {
                if(ring==otherRing && slot==other)continue;
                var b=DistrictRings.site(seed,otherRing,other);
                double distance=Math.hypot((a.chunkX()-b.chunkX())*16.0,(a.chunkZ()-b.chunkZ())*16.0);
                assertTrue(distance-512>=500,()->"Ring footprints approach: "+a+" / "+b);
            }
            assertTrue(DistrictRings.near(seed,a.chunkX()*16,a.chunkZ()*16,800));
        }
    }
}

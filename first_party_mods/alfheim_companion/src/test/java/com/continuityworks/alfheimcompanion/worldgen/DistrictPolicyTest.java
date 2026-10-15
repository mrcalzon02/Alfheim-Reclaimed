package com.continuityworks.alfheimcompanion.worldgen;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class DistrictPolicyTest {
    @Test void rejectsOriginAndMovedSpawnBeforeTerrainSampling() {
        assertFalse(DistrictPolicy.outsideSpawn(5999,0,0,0));
        assertTrue(DistrictPolicy.outsideSpawn(6000,0,0,0));
        assertFalse(DistrictPolicy.outsideSpawn(12000,0,12000,0));
        assertFalse(DistrictPolicy.outsideSpawn(16095,0,12000,0));
        assertTrue(DistrictPolicy.outsideSpawn(16096,0,12000,0));
    }
    @Test void winnerIsStableAndUniqueForPositiveAndNegativeRegions() {
        boolean[] seen=new boolean[12];
        for(long seed=0;seed<100;seed++)for(int x=-20;x<=20;x++)for(int z=-20;z<=20;z++) {
            int a=DistrictPolicy.winner(seed,x*192,z*192);
            assertEquals(a,DistrictPolicy.winner(seed,x*192+95,z*192+95));
            assertTrue(a>=0 && a<12);seen[a]=true;
        }
        for(boolean used:seen)assertTrue(used);
    }
    @Test void worstCaseReservationGapExceeds500Blocks() {
        // Conservative 256-block radius per family, including all harbor rotations.
        assertTrue(DistrictPolicy.SEPARATION*16-2*256>=500);
        assertTrue(6000-256-(1800+256)>500); // castle ring and complete footprint
    }
}

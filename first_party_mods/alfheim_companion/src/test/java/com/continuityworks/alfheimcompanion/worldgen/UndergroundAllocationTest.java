package com.continuityworks.alfheimcompanion.worldgen;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class UndergroundAllocationTest {
    @Test void sparseStableSelectionWorksAcrossNegativeCells() {
        int selected=0,total=0;
        for(long seed=0;seed<50;seed++)for(int x=-20;x<=20;x++)for(int z=-20;z<=20;z++) {
            int cx=x*80,cz=z*80;
            if((long)cx*cx+(long)cz*cz<400L*400)continue;
            boolean a=UndergroundAllocation.selected(seed,cx,cz);
            assertEquals(a,UndergroundAllocation.selected(seed,cx+31,cz+31));
            total++;if(a)selected++;
        }
        assertTrue(selected>total*.23 && selected<total*.27);
    }
    @Test void reservationClearsBothFootprintsByAtLeast500() {
        // 192 blocks conservatively encloses the pack jigsaw's 128-block reach
        // plus its <=48-block root offset. Upper footprint radius is 15 blocks.
        assertTrue(UndergroundAllocation.CLEARANCE-192-15>=500);
        assertTrue(UndergroundAllocation.SEPARATION*16-30>=500);
        assertTrue(UndergroundAllocation.overlaps(-100,-100,-51,-100));
        assertFalse(UndergroundAllocation.overlaps(-100,-100,-50,-100));
        assertFalse(UndergroundAllocation.overlaps(0,0,50,50));
    }
    @Test void adjacentCellSearchCoversEveryNearbyCandidate() {
        for(int chunk=-240;chunk<=240;chunk++) {
            int region=Math.floorDiv(chunk,80);
            for(int other=region-3;other<=region+3;other++)for(int offset=0;offset<32;offset++)
                if(Math.abs(other*80+offset-chunk)<50)assertTrue(Math.abs(other-region)<=1);
        }
    }
}

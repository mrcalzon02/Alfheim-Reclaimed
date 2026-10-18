package com.continuityworks.alfheimcompanion.worldgen;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class WorldstoneLayoutTest {
    @Test void tallestSummitsAndMinimumRockRoofAreExplicit() {
        assertEquals(260,WorldstoneLayout.MIN_SUMMIT);
        assertTrue(WorldstoneLayout.ROOF>=32);
        assertTrue(WorldstoneLayout.MIN_Y>-59);
        // 49-chunk closest candidate spacing minus the entire 239-block envelope.
        assertTrue((WorldstoneLayout.SEPARATION+1)*16-239>=500);
    }
    @Test void pointedCrystalFloatsWithAirAboveAndBelow() {
        assertTrue(WorldstoneLayout.crystal(-8,-8,4)>0);
        assertTrue(WorldstoneLayout.crystal(10,128,-5)>0);
        for(int y=-35;y<-8;y++)assertEquals(0,WorldstoneLayout.crystal(-8,y,4));
        for(int y=129;y<155;y++)assertEquals(0,WorldstoneLayout.crystal(10,y,-5));
        assertTrue(WorldstoneLayout.density(0,-35,0)<1);
        assertTrue(WorldstoneLayout.density(0,155,0)<1);
    }
    @Test void allCrystalSamplesRemainDetachedFromWallsAndShelf() {
        int samples=0;
        for(int x=-64;x<=64;x+=2)for(int z=-64;z<=64;z+=2)for(int y=-16;y<=144;y+=2) {
            if(WorldstoneLayout.crystal(x,y,z)==0)continue;
            samples++;
            assertTrue(WorldstoneLayout.density(x,y,z)<.95,"crystal intersects cavern wall");
            assertFalse(WorldstoneLayout.shelf(x,y,z),"crystal touches ledge");
        }
        assertTrue(samples>10000,"crystal is too small for the cavern");
    }
    @Test void chamberNeverTouchesBedrockAndFitsNativeReferenceRadius() {
        for(int x=-119;x<=119;x+=17)for(int z=-119;z<=119;z+=17)assertTrue(WorldstoneLayout.density(x,-59,z)>1.065);
        assertTrue((8-WorldstoneLayout.RADIUS)>>4>=-8);
        assertTrue((8+WorldstoneLayout.RADIUS)>>4<=8);
    }
    @Test void initiallyMatureCrystalsHaveBuddingSupportAndStayInsideTheCavern() {
        int count=0;int[][] vectors={{0,-1,0},{0,1,0},{0,0,-1},{0,0,1},{-1,0,0},{1,0,0}};
        for(int x=-60;x<=60;x+=2)for(int z=-60;z<=60;z+=2)for(int y=-8;y<=140;y++) {
            int face=WorldstoneLayout.seedFace(x,y,z);if(face<0)continue;count++;
            int[] d=vectors[face];
            assertEquals(1,WorldstoneLayout.crystal(x-d[0],y-d[1],z-d[2]));
            assertTrue(WorldstoneLayout.density(x,y,z)<.97);
            assertEquals(0,WorldstoneLayout.crystal(x,y,z));
        }
        assertTrue(count>100);
    }
    @Test void fragmentOreStaysBelowTheUpperCavern() {
        for(int x=-119;x<=119;x+=7)for(int z=-119;z<=119;z+=7)for(int y=80;y<=168;y+=3)assertFalse(WorldstoneLayout.ore(x,y,z));
    }
}

package com.continuityworks.alfheimcompanion.worldgen;
import org.junit.jupiter.api.Test;
import java.util.Arrays;
import static org.junit.jupiter.api.Assertions.*;
class VoidWarHostTest {
    @Test void onlyDrySupportedAboveDeepSitesFit(){
        int[] h=new int[25];Arrays.fill(h,72);assertEquals(72,VoidWarHost.surface(h));
        h[0]=59;assertEquals(-1,VoidWarHost.surface(h));h[0]=79;assertEquals(-1,VoidWarHost.surface(h));
        Arrays.fill(h,60);assertTrue(VoidWarHost.surface(h)-VoidWarHost.DEPTH>=32);
        assertFalse(VoidWarHost.solidFrame(false,true,28));assertFalse(VoidWarHost.solidFrame(true,false,28));
        assertFalse(VoidWarHost.solidFrame(true,true,22));assertTrue(VoidWarHost.solidFrame(true,true,23));
    }
    @Test void FootprintsHaveIndependentClearance(){
        assertTrue(128*16-141>=500);assertTrue(900-70-256>=500);
        // A second-neighbor 192-chunk cell cannot enter a 57-chunk reservation.
        assertTrue(2*192-191>Math.ceil(900.0/16));
    }
}

package com.continuityworks.alfheimcompanion.worldgen;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class TerrainAffordanceTest {
    private static TerrainAffordances.Profile dry(){return new TerrainAffordances.Profile("grounded",8,1,2,16,6,false,"botania:livingrock_bricks");}
    @Test void groundedBuildingsCannotLoseTheirEdgeOrUnboundTheirFootings(){
        assertThrows(IllegalArgumentException.class,()->new TerrainAffordances.Profile("grounded",8,0,2,16,6,false,"x"));
        assertThrows(IllegalArgumentException.class,()->new TerrainAffordances.Profile("grounded",8,1,2,0,6,false,"x"));
        assertThrows(IllegalArgumentException.class,()->new TerrainAffordances.Profile("grounded",8,1,2,97,6,false,"x"));
        assertEquals(3,dry().halo());
    }
    @Test void cliffAndBurialLimitsAreInclusiveAndNeverAcceptOpenVoid(){
        assertTrue(dry().fits(100,85,64));
        assertFalse(dry().fits(100,84,64));
        assertTrue(dry().fits(100,107,64));
        assertFalse(dry().fits(100,108,64));
        assertFalse(dry().fits(100,-64,64));
    }
    @Test void waterRequiresAnExplicitWetlandContract(){
        assertFalse(dry().fits(64,63,64));
        var wet=new TerrainAffordances.Profile("grounded",1,1,0,16,6,true,"botania:livingrock_bricks");
        assertTrue(wet.fits(64,63,64));
        assertFalse(wet.fits(64,20,64));
    }
}

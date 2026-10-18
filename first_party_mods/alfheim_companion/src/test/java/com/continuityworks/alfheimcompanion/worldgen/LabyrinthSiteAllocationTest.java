package com.continuityworks.alfheimcompanion.worldgen;

import org.junit.jupiter.api.Test;
import java.util.HashSet;
import java.util.ArrayDeque;
import java.util.List;
import static org.junit.jupiter.api.Assertions.*;

class LabyrinthSiteAllocationTest {
    @Test void firstFiveBandsContainManyCandidatesWithoutTheFourThousandBlockDeadZone() {
        int[] valid=new int[5];
        for(long seed=0;seed<100;seed++)for(int ring=1;ring<=5;ring++)
            for(int slot=0;slot<4;slot++) {
                var s=LabyrinthSiteAllocation.site(seed,ring,slot);
                assertEquals(ring,s.act());
                assertEquals(s,LabyrinthSiteAllocation.at(seed,s.chunkX(),s.chunkZ()).orElseThrow());
                assertTrue(s.x()*1.0*s.x()+s.z()*1.0*s.z()>=1000.0*1000);
                if(LabyrinthSiteAllocation.clearsDistricts(seed,s)
                    && LabyrinthSiteAllocation.clearsCourt(s))valid[ring-1]++;
            }
        for(int count:valid)assertTrue(count>=150, "Some act band lost all practical candidates: "+count);
    }
    @Test void collisionPredicateHandlesDiagonalOverlaps() {
        // Probe one district node at a diagonal offset: a radial-only policy
        // would permit this intersection because hypot(450,450)>544.
        var d=DistrictRings.site(42,3,1);
        int x=d.chunkX()*16+450,z=d.chunkZ()*16+450;
        assertFalse(WorldSiteAllocation.clearDistricts(42,x,z,160,128));
        assertTrue(WorldSiteAllocation.clearDistricts(42,d.chunkX()*16+600,d.chunkZ()*16+600,160,128));
    }
    @Test void completeGraphStaysConnectedAndReachesJustAboveBedrock() {
        for(int act=1;act<=5;act++)for(long seed=0;seed<30;seed++) {
            var a=LabyrinthGraphPlan.plan(seed,act,64,-64);
            var b=LabyrinthGraphPlan.plan(seed,act,64,-64);
            assertEquals(a,b);
            assertEquals(54,a.rooms().size());
            assertEquals(-56,a.bottomY());
            assertEquals(-56,a.rooms().get(49).y());
            assertEquals("boss_sanctuary",a.rooms().get(49).role());
            var neighbors=new java.util.ArrayList<java.util.List<Integer>>();
            for(int i=0;i<a.rooms().size();i++)neighbors.add(new java.util.ArrayList<>());
            for(var e:a.edges()) {
                neighbors.get(e.from()).add(e.to());neighbors.get(e.to()).add(e.from());
            }
            var seen=new HashSet<Integer>();var queue=new ArrayDeque<Integer>();
            seen.add(4);queue.add(4);
            while(!queue.isEmpty())
                for(int n:neighbors.get(queue.remove()))
                    if(seen.add(n))queue.add(n);
            assertEquals(54,seen.size());
            assertEquals(5,a.edges().stream().filter(e->e.connection().equals("vertical_stair")).count());
        }
    }
}

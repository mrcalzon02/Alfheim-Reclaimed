package com.continuityworks.alfheimcompanion.worldgen;

import org.junit.jupiter.api.Test;
import java.util.ArrayDeque;
import java.util.HashSet;
import java.util.Set;
import static org.junit.jupiter.api.Assertions.*;

class MonasteryVillageGeometryTest {
    private static boolean walkable(int x,int z) {
        var floor=MonasteryVillageGeometry.village(x,4,z);
        return (floor==MonasteryVillageGeometry.Cell.PAVING
            || floor==MonasteryVillageGeometry.Cell.ROAD_TRIM)
            && MonasteryVillageGeometry.village(x,5,z)==MonasteryVillageGeometry.Cell.AIR
            && MonasteryVillageGeometry.village(x,6,z)==MonasteryVillageGeometry.Cell.AIR;
    }
    private static Set<Integer> reachable(int sx,int sz) {
        var visited=new HashSet<Integer>();
        var queue=new ArrayDeque<Integer>();
        assertTrue(walkable(sx,sz),"Stall interior obstructed at "+sx+","+sz);
        int first=sz*65+sx;
        visited.add(first);queue.add(first);
        while(!queue.isEmpty()) {
            int p=queue.remove(),x=p%65,z=p/65;
            for(int[] d:new int[][]{{1,0},{-1,0},{0,1},{0,-1}}) {
                int nx=x+d[0],nz=z+d[1],n=nz*65+nx;
                if(nx>=0 && nx<65 && nz>=0 && nz<73 && !visited.contains(n)
                    && walkable(nx,nz)) {visited.add(n);queue.add(n);}
            }
        }
        return visited;
    }
    @Test void sixVendorInteriorsReachServiceRoadAndMonasteryApron() {
        int stalls=0;
        for(int sx:MonasteryVillageGeometry.STALL_X)
            for(int sz:MonasteryVillageGeometry.STALL_Z) {
                stalls++;
                var seen=reachable(sx+6,sz+8);
                assertTrue(seen.contains(36*65+(sx+6)),"No road from stall "+sx+","+sz);
                assertTrue(seen.contains(36*65),"No route to monastery apron from "+sx+","+sz);
                int doorZ=sz==5?23:49;
                for(int dx=5;dx<=7;dx++)for(int y=5;y<=8;y++)
                    assertEquals(MonasteryVillageGeometry.Cell.AIR,
                        MonasteryVillageGeometry.village(sx+dx,y,doorZ));
            }
        assertEquals(6,stalls);
    }
    @Test void pathsHaveFourDeepSupportAndTwoBlockHeadroomAcrossChunkSeams() {
        int supported=0,crossings=0;
        for(int x=0;x<65;x++)for(int z=0;z<73;z++) {
            if(!MonasteryVillageGeometry.road(x,z) && !MonasteryVillageGeometry.lane(x,z))continue;
            supported++;
            for(int y=0;y<=3;y++)assertEquals(MonasteryVillageGeometry.Cell.FOUNDATION,
                MonasteryVillageGeometry.village(x,y,z),"Unsupported path "+x+","+z);
            assertTrue(walkable(x,z),"Obstructed path "+x+","+z);
            for(int offset=0;offset<16;offset++) {
                int worldX=x+offset,worldZ=z+offset;
                if(Math.floorDiv(worldX,16)!=Math.floorDiv(worldX+1,16)
                    || Math.floorDiv(worldZ,16)!=Math.floorDiv(worldZ+1,16))crossings++;
            }
        }
        assertTrue(supported>400);
        assertTrue(crossings>0);
        for(int y=0;y<=3;y++)assertEquals(MonasteryVillageGeometry.Cell.FOUNDATION,
            MonasteryVillageGeometry.approach(y));
        assertEquals(MonasteryVillageGeometry.Cell.PAVING,MonasteryVillageGeometry.approach(4));
        assertEquals(MonasteryVillageGeometry.Cell.AIR,MonasteryVillageGeometry.approach(5));
        assertEquals(MonasteryVillageGeometry.Cell.AIR,MonasteryVillageGeometry.approach(6));
    }
    @Test void blockedCellsAndWetVoidOrCliffTerrainAreRejected() {
        assertFalse(walkable(6,5)); // solid corner wall
        assertFalse(walkable(12,14)); // existing decorative barrel
        assertFalse(walkable(0,0)); // untouched ground, not a route
        assertTrue(MonasteryVillageGeometry.terrainHeightOK(65,63,65));
        assertFalse(MonasteryVillageGeometry.terrainHeightOK(65,63,63)); // submerged
        assertFalse(MonasteryVillageGeometry.terrainHeightOK(65,63,59)); // deep drop
        assertFalse(MonasteryVillageGeometry.terrainHeightOK(65,63,70)); // cliff
        assertTrue(MonasteryVillageGeometry.terrainFootingOK(true,true));
        assertFalse(MonasteryVillageGeometry.terrainFootingOK(false,true)); // water
        assertFalse(MonasteryVillageGeometry.terrainFootingOK(true,false)); // void/unsupported
    }
}

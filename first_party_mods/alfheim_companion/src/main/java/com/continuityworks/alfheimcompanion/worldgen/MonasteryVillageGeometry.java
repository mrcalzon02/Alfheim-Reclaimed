package com.continuityworks.alfheimcompanion.worldgen;

/**
 * Pure block-by-block plan for the monastery village and its connecting apron.
 * Coordinates are relative to the village piece; Y=4 is the walking surface.
 * Keeping this Minecraft-free lets tests inspect the same cells that
 * MonasteryLabyrinthPiece actually places, including at chunk boundaries.
 */
final class MonasteryVillageGeometry {
    enum Cell { NONE, FOUNDATION, PAVING, ROAD_TRIM, AIR, WALL, FENCE, ROOF, LIGHT, BARREL }
    static final int WIDTH=65, DEPTH=73, ROAD_MIN_Z=34, ROAD_MAX_Z=38;
    static final int[] STALL_X={6,27,48}, STALL_Z={5,49};

    static boolean road(int x,int z) {
        return x>=0 && x<WIDTH && z>=ROAD_MIN_Z && z<=ROAD_MAX_Z;
    }
    static boolean lane(int x,int z) {
        if(z<23 || z>49)return false;
        for(int sx:STALL_X)if(x>=sx+5 && x<=sx+7)return true;
        return false;
    }
    static Cell village(int x,int y,int z) {
        if(x<0 || x>=WIDTH || z<0 || z>=DEPTH || y<0 || y>=22)return Cell.NONE;
        boolean shop=false,edge=false,door=false,light=false;
        for(int sx:STALL_X)for(int sz:STALL_Z)
            if(x>=sx && x<sx+13 && z>=sz && z<sz+19) {
                shop=true;
                int dx=x-sx,dz=z-sz;
                edge=dx==0 || dx==12 || dz==0 || dz==18;
                door=dx>=5 && dx<=7 && (sz==5?dz==18:dz==0)
                    && y>=5 && y<=8;
                light=dx==6 && dz==9 && y==12;
            }
        boolean road=road(x,z),lane=lane(x,z);
        if(!shop && !road && !lane)return Cell.NONE;
        // The old code paved road and lanes at Y=4 but placed no blocks below.
        // Permitted terrain relief could leave floating paths.
        if(y<=3)return Cell.FOUNDATION;
        if(y==4)return shop?Cell.PAVING:road?Cell.ROAD_TRIM:Cell.PAVING;
        if(!shop)return Cell.AIR;
        if(y==13)return Cell.ROOF;
        if(y>=5 && y<=12) {
            if(door)return Cell.AIR;
            if(edge)return y<11?Cell.WALL:Cell.FENCE;
            if(light)return Cell.LIGHT;
            if(y==5 && z%44==14 && x%21==12)return Cell.BARREL;
            return Cell.AIR;
        }
        return Cell.NONE;
    }
    /** Apron floor is at the same Y=4 datum as both adjacent structures. */
    static Cell approach(int y) {
        if(y<0 || y>=10)return Cell.NONE;
        if(y<=3)return Cell.FOUNDATION;
        if(y==4)return Cell.PAVING;
        return Cell.AIR;
    }
    static boolean terrainHeightOK(int reference,int sea,int y) {
        return y>sea && Math.abs((long)y-reference)<=4;
    }
    static boolean terrainFootingOK(boolean surfaceDry,boolean fiveSolidDryLayers) {
        return surfaceDry && fiveSolidDryLayers;
    }
    private MonasteryVillageGeometry() {}
}

package com.continuityworks.alfheimcompanion.worldgen;

/** Stateless reservations shared by upper discoveries and the pack's own dungeons. */
public final class UndergroundAllocation {
    public static final int SPACING=80, SEPARATION=48, SALT=202610151, CLEARANCE=800;
    public static boolean selected(long seed,int chunkX,int chunkZ) {
        long value=seed ^ ((long)Math.floorDiv(chunkX,SPACING)*0x9E3779B97F4A7C15L)
            ^ ((long)Math.floorDiv(chunkZ,SPACING)*0xD1B54A32D192ED03L);
        value=(value^(value>>>30))*0xBF58476D1CE4E5B9L;
        value=(value^(value>>>27))*0x94D049BB133111EBL;
        int x=chunkX*16,z=chunkZ*16;
        return ((value^(value>>>31))&3)==0
            && WorldSiteAllocation.outsideCourt(x,z,15,WorldSiteAllocation.GAP);
    }
    public static boolean overlaps(int chunkX,int chunkZ,int upperX,int upperZ) {
        return Math.abs(((long)chunkX-upperX)*16)<CLEARANCE
            && Math.abs(((long)chunkZ-upperZ)*16)<CLEARANCE;
    }
    private UndergroundAllocation() {}
}

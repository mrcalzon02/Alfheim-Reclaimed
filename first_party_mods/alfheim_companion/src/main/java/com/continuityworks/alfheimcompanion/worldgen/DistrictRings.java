package com.continuityworks.alfheimcompanion.worldgen;

import java.util.Optional;

/** Four staggered sites per kilometre ring, centred on the fixed starting hub. */
public final class DistrictRings {
    public static final int INTERVAL=1000, CELL_CHUNKS=32, SITES=4, ACTIVE_FAMILIES=9;
    public record Site(int ring,int slot,int chunkX,int chunkZ,int family) {}
    private static long mix(long n) {
        n=(n^(n>>>30))*0xBF58476D1CE4E5B9L;
        n=(n^(n>>>27))*0x94D049BB133111EBL;
        return n^(n>>>31);
    }
    public static Site site(long seed,int ring,int slot) {
        if(ring<1 || slot<0 || slot>=SITES)throw new IllegalArgumentException("Invalid ring site");
        long h=mix(seed^202610180L);
        double angle=(h>>>11)*0x1.0p-53*Math.PI*2+slot*Math.PI/2+(ring%2==0?Math.PI/4:0);
        int x=(int)Math.round(ring*(double)INTERVAL*Math.cos(angle)/16);
        int z=(int)Math.round(ring*(double)INTERVAL*Math.sin(angle)/16);
        int family=Math.floorMod((int)Math.floorMod(h,ACTIVE_FAMILIES)+(ring-1)*SITES+slot,ACTIVE_FAMILIES);
        return new Site(ring,slot,x,z,family);
    }
    public static Optional<Site> inCell(long seed,int chunkX,int chunkZ) {
        int rx=Math.floorDiv(chunkX,CELL_CHUNKS),rz=Math.floorDiv(chunkZ,CELL_CHUNKS);
        int nearest=(int)Math.round(Math.hypot(rx*512.0+256,rz*512.0+256)/INTERVAL);
        for(int ring=Math.max(1,nearest-1);ring<=nearest+1;ring++)for(int slot=0;slot<SITES;slot++) {
            var s=site(seed,ring,slot);
            if(Math.floorDiv(s.chunkX,CELL_CHUNKS)==rx && Math.floorDiv(s.chunkZ,CELL_CHUNKS)==rz)return Optional.of(s);
        }
        return Optional.empty();
    }
    public static Optional<Site> at(long seed,int chunkX,int chunkZ) {
        return inCell(seed,chunkX,chunkZ).filter(s->s.chunkX==chunkX && s.chunkZ==chunkZ);
    }
    /**
     * Square-envelope collision used by every large build family. A circular
     * centre-distance check is insufficient: two axis-aligned 320-block sites
     * can intersect diagonally while their centres remain more than R apart.
     * This calculation is deterministic and never asks for generated chunks.
     */
    public static boolean nearEnvelope(long seed,int x,int z,int clearance) {
        int nearest=(int)Math.round(Math.hypot(x,z)/INTERVAL);
        int reach=(int)Math.ceil(Math.sqrt(2.0)*clearance/INTERVAL)+2;
        for(int ring=Math.max(1,nearest-reach);ring<=nearest+reach;ring++)
            for(int slot=0;slot<SITES;slot++) {
                var s=site(seed,ring,slot);
                long dx=(long)s.chunkX()*16-x,dz=(long)s.chunkZ()*16-z;
                if(Math.abs(dx)<clearance && Math.abs(dz)<clearance)return true;
            }
        return false;
    }
    public static boolean near(long seed,int x,int z,int clearance) {
        int nearest=(int)Math.round(Math.hypot(x,z)/INTERVAL);
        int reach=(int)Math.ceil(clearance/(double)INTERVAL)+1;
        for(int ring=Math.max(1,nearest-reach);ring<=nearest+reach;ring++)for(int slot=0;slot<SITES;slot++) {
            var s=site(seed,ring,slot);
            long dx=(long)s.chunkX*16-x,dz=(long)s.chunkZ*16-z;
            if(dx*dx+dz*dz<(long)clearance*clearance)return true;
        }
        return false;
    }
    private DistrictRings() {}
}

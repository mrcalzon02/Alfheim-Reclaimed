package com.continuityworks.alfheimcompanion.worldgen;

import java.util.Optional;

/**
 * Interleaved monastery candidates in the SAME kilometre-ring allocator used
 * by existing districts. These are future candidate reservations, not active
 * structures: no phantom carve-outs until a real monastery is registered.
 * Keep the four existing district slots and family hash completely unchanged.
 */
public final class LabyrinthSiteAllocation {
    public static final int SITES_PER_RING=4;
    public static final int OFFSET_FROM_DISTRICT_RING=340;
    public static final int HALF_WIDTH=160;
    public static final int GAP=WorldSiteAllocation.GAP;
    public record Site(int ring,int slot,int chunkX,int chunkZ,int act) {
        public int x(){return chunkX*16+8;}
        public int z(){return chunkZ*16+8;}
    }
    private LabyrinthSiteAllocation(){}

    /**
     * Districts occupy the four principal azimuths at radii 1000, 2000...
     * Monasteries take intercardinal azimuths at radii 1340, 2340...
     * The 340-block offset avoids the total candidate starvation caused by
     * putting sites exactly 500 blocks between adjacent reserved rings.
     */
    public static Site site(long seed,int ring,int slot) {
        if(ring<1 || slot<0 || slot>=SITES_PER_RING)
            throw new IllegalArgumentException("Invalid monastery ring/slot");
        var anchor=DistrictRings.site(seed,ring,slot);
        double angle=Math.atan2(anchor.chunkZ(),anchor.chunkX())+Math.PI/4.0;
        double radius=ring*(double)DistrictRings.INTERVAL+OFFSET_FROM_DISTRICT_RING;
        int cx=(int)Math.round(radius*Math.cos(angle)/16.0);
        int cz=(int)Math.round(radius*Math.sin(angle)/16.0);
        int act=WorldSiteAllocation.dungeonAct(cx*16+8,cz*16+8);
        return new Site(ring,slot,cx,cz,act);
    }
    public static Optional<Site> inCell(long seed,int chunkX,int chunkZ) {
        int cellX=Math.floorDiv(chunkX,DistrictRings.CELL_CHUNKS);
        int cellZ=Math.floorDiv(chunkZ,DistrictRings.CELL_CHUNKS);
        double x=cellX*DistrictRings.CELL_CHUNKS*16.0+256;
        double z=cellZ*DistrictRings.CELL_CHUNKS*16.0+256;
        int ringGuess=(int)Math.floor((Math.hypot(x,z)-OFFSET_FROM_DISTRICT_RING)
            /DistrictRings.INTERVAL);
        for(int ring=Math.max(1,ringGuess-2);ring<=ringGuess+2;ring++)
            for(int slot=0;slot<SITES_PER_RING;slot++) {
                Site site=site(seed,ring,slot);
                if(Math.floorDiv(site.chunkX(),DistrictRings.CELL_CHUNKS)==cellX
                    && Math.floorDiv(site.chunkZ(),DistrictRings.CELL_CHUNKS)==cellZ)
                    return Optional.of(site);
            }
        return Optional.empty();
    }
    public static Optional<Site> at(long seed,int chunkX,int chunkZ) {
        return inCell(seed,chunkX,chunkZ)
            .filter(s->s.chunkX()==chunkX && s.chunkZ()==chunkZ);
    }
    /** Both structures must clear their entire square footprint, plus gap. */
    public static boolean nearEnvelope(long seed,int x,int z,int clearance) {
        int nearest=(int)Math.floor((Math.hypot(x,z)-OFFSET_FROM_DISTRICT_RING)
            /DistrictRings.INTERVAL);
        int reach=(int)Math.ceil(Math.sqrt(2.0)*clearance/DistrictRings.INTERVAL)+3;
        for(int ring=Math.max(1,nearest-reach);ring<=nearest+reach;ring++)
            for(int slot=0;slot<SITES_PER_RING;slot++) {
                Site s=site(seed,ring,slot);
                if(Math.abs((long)s.x()-x)<clearance
                    && Math.abs((long)s.z()-z)<clearance)return true;
            }
        return false;
    }
    /** Pure cheap rejection; reserve only once the compound structure exists. */
    public static boolean clearsDistricts(long seed,Site site) {
        return WorldSiteAllocation.clearDistricts(seed,site.x(),site.z(),
            HALF_WIDTH,GAP);
    }
    public static boolean clearsCourt(Site site) {
        return WorldSiteAllocation.outsideCourt(site.x(),site.z(),HALF_WIDTH,GAP);
    }
}

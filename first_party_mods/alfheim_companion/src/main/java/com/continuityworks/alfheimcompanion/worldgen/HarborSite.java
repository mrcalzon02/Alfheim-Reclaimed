package com.continuityworks.alfheimcompanion.worldgen;

import java.util.Optional;
import java.util.function.Consumer;
import java.util.function.LongSupplier;
import java.util.HashMap;

/** Read-only placement policy shared by generated terrain and checked commands. */
public final class HarborSite {
    public record Column(int surface, int floor, boolean water) {}
    public interface Sampler { Column sample(int x, int z); }
    public record Site(int x, int z, int baseY, int rotation, int quayLift) {}
    public record Attempt(int rotation,int lift,int requests,int lastX,int lastZ,Column lastColumn,boolean accepted) {}
    public static final int GENERATION_COLUMN_LIMIT=32;
    public static final long GENERATION_TIME_LIMIT=150_000_000L;
    public record BoundedResult(Optional<Site> site,int columns,String outcome) {}

    /** Approximate generation policy: fixed probes, never an exhaustive search. */
    public static BoundedResult findBounded(int x,int z,int sea,Sampler sampler,HarborGeometry.Part[] parts,
            LongSupplier clock,int columnLimit,long timeLimit) {
        long start=clock.getAsLong();var cache=new HashMap<Long,Column>();
        String[] stopped={null};
        Sampler limited=(px,pz)-> {
            if(stopped[0]!=null)return null;
            if(clock.getAsLong()-start>=timeLimit) {stopped[0]="time_budget";return null;}
            long key=((long)px<<32)^(pz&0xffffffffL);
            if(cache.containsKey(key))return cache.get(key);
            if(cache.size()>=columnLimit) {stopped[0]="column_budget";return null;}
            Column c=sampler.sample(px,pz);cache.put(key,c);
            if(clock.getAsLong()-start>=timeLimit) {stopped[0]="time_budget";return null;}
            return c;
        };
        for(int r=0;r<4 && stopped[0]==null;r++) {
            if(!check(x,z,sea,r,23,-20,true,limited,false,6))continue;
            if(!check(x,z,sea,r,23,23,false,limited,false,6) || !check(x,z,sea,r,23,100,false,limited,false,6))continue;
            int lift=0;
            int[] center=HarborGeometry.rotate(23,23,r),approach=HarborGeometry.rotate(23,100,r);
            Column a=limited.sample(x+center[0],z+center[1]),b=limited.sample(x+approach[0],z+approach[1]);
            if(a==null||b==null)break;
            while(lift<6 && Math.max(a.surface(),b.surface())>sea+3+lift)lift+=2;
            boolean usable=true;
            for(var part:parts) {
                int[] at=HarborGeometry.rotate((part.minX()+part.maxX())/2,(part.minZ()+part.maxZ())/2,r);
                Column c=limited.sample(x+at[0],z+at[1]);
                // Representative centers reject gross void/cliffs; local gaps and clipping are allowed.
                if(c==null || c.surface()<sea-16 || c.floor()<sea-24 || c.surface()>sea+24) {usable=false;break;}
            }
            if(stopped[0]!=null)break;
            if(usable)return new BoundedResult(Optional.of(new Site(x,z,sea-6+lift,r,lift)),cache.size(),"accepted_approximate");
        }
        return new BoundedResult(Optional.empty(),cache.size(),stopped[0]==null?"unsuitable_anchors":stopped[0]);
    }

    public static Optional<Site> find(int x, int z, int sea, Sampler sampler) {
        return find(x,z,sea,sampler,HarborGeometry.PARTS);
    }
    public static Optional<Site> find(int x,int z,int sea,Sampler sampler,HarborGeometry.Part[] parts) {
        return find(x,z,sea,sampler,parts,null);
    }
    public static Optional<Site> find(int x,int z,int sea,Sampler sampler,HarborGeometry.Part[] parts,Consumer<Attempt> observer) {
        for (int r=0;r<4;r++) for(int lift:new int[]{0,2,4,6}) {
            int[] last=observer==null?null:new int[3];Column[] value=observer==null?null:new Column[1];
            Sampler checked=observer==null?sampler:(px,pz)-> {
                last[0]=px;last[1]=pz;last[2]++;value[0]=sampler.sample(px,pz);return value[0];
            };
            boolean accepted=valid(x,z,sea,r,checked,lift,parts);
            if(observer!=null) observer.accept(new Attempt(r,lift,last[2],last[0],last[1],value[0],accepted));
            if(accepted) return Optional.of(new Site(x,z,sea-6+lift,r,lift));
        }
        return Optional.empty();
    }

    public static boolean valid(int x, int z, int sea, int r, Sampler sampler) {
        return valid(x,z,sea,r,sampler,0);
    }
    public static boolean valid(int x,int z,int sea,int r,Sampler sampler,int lift) {
        return valid(x,z,sea,r,sampler,lift,HarborGeometry.PARTS);
    }
    private static boolean valid(int x,int z,int sea,int r,Sampler sampler,int lift,HarborGeometry.Part[] parts) {
        // Cheap wet/dry probes reject inland, deep ocean and reversed coast before a full scan.
        if (!check(x,z,sea,r,23,-20,true,sampler,false,lift) || !check(x,z,sea,r,23,23,false,sampler,false,lift) || !check(x,z,sea,r,23,100,false,sampler,false,lift)) return false;
        // Refine across the whole district before scanning every column. Native
        // column values are cached by the caller, so repeated lattice points are cheap.
        for(int stride:new int[]{8,4,2,1}) for (HarborGeometry.Part part: parts) {
            for (int px=part.minX();;px=Math.min(px+stride,part.maxX())) {
                for (int pz=part.minZ();;pz=Math.min(pz+stride,part.maxZ())) {
                    if (!check(x,z,sea,r,px,pz,part.maritime(),sampler,(pz>=-16 && pz<16) || !part.maritime(),lift)) return false;
                    if (pz==part.maxZ()) break;
                }
                if (px==part.maxX()) break;
            }
        }
        // The final stride is one: narrow hazards still cannot slip between probes.
        return true;
    }

    private static boolean check(int x,int z,int sea,int r,int px,int pz,boolean wet,Sampler sampler) {
        return check(x,z,sea,r,px,pz,wet,sampler,false,0);
    }
    private static boolean check(int x,int z,int sea,int r,int px,int pz,boolean wet,Sampler sampler,boolean apron,int lift) {
        int[] at=HarborGeometry.rotate(px,pz,r);
        Column c=sampler.sample(x+at[0],z+at[1]);
        if (c==null) return false; // Missing/unloaded columns are never assumed safe.
        if ((wet && !apron) || (apron && c.water())) return c.water() && c.surface()==sea && c.floor()>=sea-6 && c.floor()<sea;
        // Dry banks may sit below sea level; the actual lowest footing must reach them.
        return !c.water() && c.surface()>=sea-6 && c.surface()<=sea+3+lift && c.floor()>=sea-6;
    }
    private HarborSite() {}
}

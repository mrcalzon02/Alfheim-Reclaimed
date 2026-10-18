package com.continuityworks.alfheimcompanion.worldgen;

import java.util.ArrayList;
import java.util.List;

/**
 * Immutable, seed-reproducible topological plan; NOT a structure generator.
 * The real pieces, vendors, encounter controllers and saved-world records must
 * implement this contract before the dungeon can be registered for worldgen.
 * Horizontal cells are 56 blocks apart; 48-block room templates leave an
 * eight-block connector gap. Six strata run from the surface to natural bedrock.
 */
public final class LabyrinthGraphPlan {
    public static final int LAYERS=6, ROOMS_PER_LAYER=9, CELL_PITCH=56;
    public static final int ROOM_MAX_HORIZONTAL=48, ROOM_MAX_HEIGHT=18;
    public record Room(int id,int layer,int x,int y,int z,String role) {}
    public record Edge(int from,int to,String connection) {}
    public record Plan(long seed,int act,int surfaceY,int bottomY,List<Room> rooms,List<Edge> edges) {}
    private LabyrinthGraphPlan(){}
    private static long mix(long n) {
        n=(n^(n>>>30))*0xBF58476D1CE4E5B9L;
        n=(n^(n>>>27))*0x94D049BB133111EBL;
        return n^(n>>>31);
    }
    /** Coordinates are local to one reserved monastery envelope. */
    public static Plan plan(long seed,int act,int surfaceY,int minBuildY) {
        if(act<1 || act>5)throw new IllegalArgumentException("Unsupported act");
        int upper=surfaceY-12,bottom=minBuildY+8;
        if(upper-bottom<5*ROOM_MAX_HEIGHT)
            throw new IllegalArgumentException("Insufficient height for full-depth labyrinth");
        List<Room> rooms=new ArrayList<>(LAYERS*ROOMS_PER_LAYER);
        List<Edge> edges=new ArrayList<>();
        long h=mix(seed^0x5A6F1C20261018L);
        for(int layer=0;layer<LAYERS;layer++) {
            int y=upper-((upper-bottom)*layer)/(LAYERS-1);
            for(int row=0;row<3;row++)for(int col=0;col<3;col++) {
                int local=row*3+col,id=layer*ROOMS_PER_LAYER+local;
                String role=layer==LAYERS-1&&local==4?"boss_sanctuary":
                    layer==0&&local==4?"entrance_landing":
                    local==4?"descent_hub":
                    local%2==0?"chamber":"gallery";
                rooms.add(new Room(id,layer,(col-1)*CELL_PITCH,y,
                                   (row-1)*CELL_PITCH,role));
            }
            int base=layer*ROOMS_PER_LAYER;
            // Every room has a guaranteed return path to the central hub.
            for(int[] pair:new int[][]{{4,1},{4,3},{4,5},{4,7},
                                       {0,1},{2,1},{6,7},{8,7}})
                edges.add(new Edge(base+pair[0],base+pair[1],"walkway"));
            // One branch-loop per tier prevents a line of dead ends while
            // preserving a connected mandatory graph.
            if(((h>>>layer)&1L)==0L) {
                edges.add(new Edge(base+0,base+3,"side_passage"));
                edges.add(new Edge(base+6,base+3,"side_passage"));
            } else {
                edges.add(new Edge(base+2,base+5,"side_passage"));
                edges.add(new Edge(base+8,base+5,"side_passage"));
            }
            if(layer>0)
                edges.add(new Edge((layer-1)*ROOMS_PER_LAYER+4,base+4,"vertical_stair"));
        }
        return new Plan(seed,act,surfaceY,bottom,List.copyOf(rooms),List.copyOf(edges));
    }
}

package com.continuityworks.alfheimcompanion.worldgen;

import java.util.Arrays;

/** Pure host envelope, shared by tests and native generation. */
public final class VoidWarHost {
    public static final int WIDTH=141,HALF=70,DEPTH=28,SAMPLES=25;
    public static int surface(int[] heights) {
        if(heights.length!=SAMPLES)return -1;
        int[] sorted=heights.clone();Arrays.sort(sorted);
        if(sorted[0]<60 || sorted[24]>160 || sorted[24]-sorted[0]>6)return -1;
        return sorted[12];
    }
    public static boolean solidFrame(boolean floor,boolean roof,int solid) {return floor && roof && solid>=23;}
    private VoidWarHost() {}
}

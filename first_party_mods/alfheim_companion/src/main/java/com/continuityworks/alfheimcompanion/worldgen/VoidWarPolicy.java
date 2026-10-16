package com.continuityworks.alfheimcompanion.worldgen;

import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.placement.RandomSpreadStructurePlacement;
import net.minecraft.world.level.levelgen.structure.placement.RandomSpreadType;

/** Rare shared reservations. No height scans, chunk loads, retries or mutable claims. */
public final class VoidWarPolicy {
    public static final int SPACING=192,SEPARATION=128,SALT=202610153,CLEARANCE=900;
    public static final TagKey<Biome> BIOMES=TagKey.create(Registries.BIOME,new ResourceLocation("alfheim","has_void_war_remnants"));
    static final RandomSpreadStructurePlacement GRID=new RandomSpreadStructurePlacement(SPACING,SEPARATION,RandomSpreadType.LINEAR,SALT);
    public static int choice(long seed,int chunkX,int chunkZ,boolean wide) {
        long v=seed^((long)Math.floorDiv(chunkX,SPACING)*0x9E3779B97F4A7C15L)^((long)Math.floorDiv(chunkZ,SPACING)*0xD1B54A32D192ED03L);
        v=(v^(v>>>30))*0xBF58476D1CE4E5B9L;v=(v^(v>>>27))*0x94D049BB133111EBL;v^=v>>>31;
        return wide?(int)Math.floorMod(v,6):6+(int)Math.floorMod(v,2);
    }
    static int winner(Structure.GenerationContext c) {
        int x=c.chunkPos().getMiddleBlockX(),z=c.chunkPos().getMiddleBlockZ();boolean wide=true;
        for(int dx:new int[]{-70,70})for(int dz:new int[]{-70,70})
            wide&=c.biomeSource().getNoiseBiome((x+dx)>>2,16,(z+dz)>>2,c.randomState().sampler()).is(BIOMES);
        return choice(c.seed(),c.chunkPos().x,c.chunkPos().z,wide);
    }
    static boolean eligible(Structure.GenerationContext c,net.minecraft.world.level.ChunkPos p) {
        long x=p.getMiddleBlockX(),z=p.getMiddleBlockZ();
        return x*x+z*z>=5000L*5000 && c.biomeSource().getNoiseBiome((int)x>>2,16,(int)z>>2,c.randomState().sampler()).is(BIOMES);
    }
    static boolean reserved(Structure.GenerationContext c) {
        int rx=Math.floorDiv(c.chunkPos().x,SPACING),rz=Math.floorDiv(c.chunkPos().z,SPACING);
        for(int dx=-1;dx<=1;dx++)for(int dz=-1;dz<=1;dz++) {
            var p=GRID.getPotentialStructureChunk(c.seed(),(rx+dx)*SPACING,(rz+dz)*SPACING);
            if(Math.abs(((long)c.chunkPos().x-p.x)*16)<CLEARANCE && Math.abs(((long)c.chunkPos().z-p.z)*16)<CLEARANCE
                && eligible(c,p))return true;
        }
        return false;
    }
    private VoidWarPolicy() {}
}

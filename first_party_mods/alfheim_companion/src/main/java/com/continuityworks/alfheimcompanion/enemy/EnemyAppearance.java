package com.continuityworks.alfheimcompanion.enemy;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.Mob;

/** A synchronized appearance, chosen once on spawn, retained across travel and reload. */
public final class EnemyAppearance {
    public record State(EntityDataAccessor<Integer> profile, EntityDataAccessor<Integer> style) {}
    public static State state(Class<? extends Entity> type) {
        return new State(SynchedEntityData.defineId(type,EntityDataSerializers.INT),
                         SynchedEntityData.defineId(type,EntityDataSerializers.INT));
    }
    public static void define(Mob mob,State state) {
        mob.getEntityData().define(state.profile(),23);
        mob.getEntityData().define(state.style(),0);
    }
    private static State state(Mob mob) { return ((ThemedEnemy)mob).appearanceState(); }
    public static int profile(Mob mob) { return mob.getEntityData().get(state(mob).profile()); }
    public static int style(Mob mob) { return Math.floorMod(mob.getEntityData().get(state(mob).style()),3); }
    public static void assign(Mob mob) {
        mob.getEntityData().set(state(mob).profile(),EnemyProfiles.choose(mob.level().getBiome(mob.blockPosition())));
        mob.getEntityData().set(state(mob).style(),mob.getRandom().nextInt(3));
    }
    public static void save(Mob mob,CompoundTag tag) {
        tag.putString("AlfheimBiome",EnemyProfiles.get(profile(mob)).biome());
        tag.putInt("AlfheimStyle",style(mob));
    }
    public static void load(Mob mob,CompoundTag tag) {
        int index=tag.contains("AlfheimBiome") ? EnemyProfiles.index(tag.getString("AlfheimBiome"))
                : EnemyProfiles.choose(mob.level().getBiome(mob.blockPosition()));
        mob.getEntityData().set(state(mob).profile(),index);
        mob.getEntityData().set(state(mob).style(),Math.floorMod(tag.getInt("AlfheimStyle"),3));
    }
    public static Component name(Mob mob,String species) {
        String style=new String[]{"Bound ","Shrouded ","Crowned "}[style(mob)];
        return Component.literal(EnemyProfiles.get(profile(mob)).title()+" "+style+species);
    }
    private EnemyAppearance() {}
}

package com.continuityworks.alfheimcompanion.society;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.*;
import net.minecraft.world.DifficultyInstance;

/** Passive adult civilian. Social titles are appearance identities, not companion leases. */
public final class ElvenCitizenEntity extends PathfinderMob {
    private static final EntityDataAccessor<Integer> ROLE=SynchedEntityData.defineId(ElvenCitizenEntity.class,EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> LOOK=SynchedEntityData.defineId(ElvenCitizenEntity.class,EntityDataSerializers.INT);
    public ElvenCitizenEntity(EntityType<? extends PathfinderMob> type,Level level){super(type,level);setPersistenceRequired();}
    @Override protected void defineSynchedData(){super.defineSynchedData();entityData.define(ROLE,0);entityData.define(LOOK,0);}
    public int role(){return ElvenSociety.safeRole(entityData.get(ROLE));}
    public int appearance(){return Math.floorMod(entityData.get(LOOK),4);}
    public static AttributeSupplier.Builder attributes(){return Mob.createMobAttributes().add(Attributes.MAX_HEALTH,20).add(Attributes.MOVEMENT_SPEED,.23).add(Attributes.FOLLOW_RANGE,16);}
    @Override protected void registerGoals(){
        goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(1,new PanicGoal(this,1.2));
        goalSelector.addGoal(6,new WaterAvoidingRandomStrollGoal(this,.7));
        goalSelector.addGoal(7,new LookAtPlayerGoal(this,Player.class,8));goalSelector.addGoal(8,new RandomLookAroundGoal(this));
    }
    @Override public boolean removeWhenFarAway(double distance){return false;}
    @Override protected Component getTypeName(){return Component.literal("Elven "+ElvenSociety.NAMES[role()]);}
    @Override public void addAdditionalSaveData(CompoundTag tag){super.addAdditionalSaveData(tag);tag.putString("ElfRole",ElvenSociety.IDS[role()]);tag.putInt("ElfAppearance",appearance());}
    @Override public void readAdditionalSaveData(CompoundTag tag){super.readAdditionalSaveData(tag);entityData.set(ROLE,ElvenSociety.role(tag.getString("ElfRole")));entityData.set(LOOK,Math.floorMod(tag.getInt("ElfAppearance"),4));}
    @Override public SpawnGroupData finalizeSpawn(ServerLevelAccessor level,DifficultyInstance difficulty,MobSpawnType reason,SpawnGroupData group,CompoundTag tag){
        return super.finalizeSpawn(level,difficulty,reason,group,tag);
    }
}

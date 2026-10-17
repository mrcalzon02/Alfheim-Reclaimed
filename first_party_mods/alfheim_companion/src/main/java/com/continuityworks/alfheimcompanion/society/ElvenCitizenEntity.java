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
public final class ElvenCitizenEntity extends net.minecraft.world.entity.npc.AbstractVillager {
    private static final EntityDataAccessor<Integer> ROLE=SynchedEntityData.defineId(ElvenCitizenEntity.class,EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> LOOK=SynchedEntityData.defineId(ElvenCitizenEntity.class,EntityDataSerializers.INT);
    public ElvenCitizenEntity(EntityType<? extends net.minecraft.world.entity.npc.AbstractVillager> type,Level level){super(type,level);setPersistenceRequired();}
    @Override protected void defineSynchedData(){super.defineSynchedData();entityData.define(ROLE,0);entityData.define(LOOK,0);}
    public int role(){return ElvenSociety.safeRole(entityData.get(ROLE));}
    public int appearance(){return Math.floorMod(entityData.get(LOOK),4);}
    public static AttributeSupplier.Builder attributes(){return Mob.createMobAttributes().add(Attributes.MAX_HEALTH,20).add(Attributes.MOVEMENT_SPEED,.23).add(Attributes.FOLLOW_RANGE,16);}
    private long lastRestock=-1;
    @Override public AgeableMob getBreedOffspring(net.minecraft.server.level.ServerLevel level,AgeableMob partner){return null;}
    @Override public boolean canBreed(){return false;}
    @Override public boolean showProgressBar(){return false;}
    @Override public boolean canRestock(){return true;}
    @Override protected void updateTrades(){
        offers=ElvenCitizenTrades.offers(role());
        if(lastRestock<0)lastRestock=level().getGameTime();
    }
    @Override protected void rewardTradeXp(net.minecraft.world.item.trading.MerchantOffer offer){}
    @Override public net.minecraft.world.InteractionResult mobInteract(Player player,net.minecraft.world.InteractionHand hand){
        if(hand!=net.minecraft.world.InteractionHand.MAIN_HAND||player.isSecondaryUseActive()
            ||player.getItemInHand(hand).is(net.minecraft.world.item.Items.NAME_TAG)||!isAlive()||isTrading())return super.mobInteract(player,hand);
        if(!level().isClientSide){
            restockAt(level().getGameTime());
            if(getOffers().isEmpty())return net.minecraft.world.InteractionResult.PASS;
            setTradingPlayer(player);openTradingScreen(player,getDisplayName(),1);
        }
        return net.minecraft.world.InteractionResult.sidedSuccess(level().isClientSide);
    }
    /** Uses game time, so sleeping cannot repeatedly refresh rare stock. Persisted across reloads. */
    public boolean restockAt(long now){
        if(offers==null||isTrading())return false;
        if(lastRestock<0){lastRestock=now;return false;}
        if(now<lastRestock||now-lastRestock<ElvenCitizenTrades.restockTicks())return false;
        for(var offer:offers)offer.resetUses();lastRestock=now;return true;
    }
    @Override protected void customServerAiStep(){super.customServerAiStep();restockAt(level().getGameTime());}
    @Override protected void registerGoals(){
        goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(1,new PanicGoal(this,1.2));
        goalSelector.addGoal(2,new TradeWithPlayerGoal(this));goalSelector.addGoal(3,new LookAtTradingPlayerGoal(this));
        goalSelector.addGoal(6,new WaterAvoidingRandomStrollGoal(this,.7));
        goalSelector.addGoal(7,new LookAtPlayerGoal(this,Player.class,8));goalSelector.addGoal(8,new RandomLookAroundGoal(this));
    }
    @Override public boolean removeWhenFarAway(double distance){return false;}
    @Override protected Component getTypeName(){return Component.literal("Elven "+ElvenSociety.NAMES[role()]);}
    @Override public void addAdditionalSaveData(CompoundTag tag){super.addAdditionalSaveData(tag);tag.putString("ElfRole",ElvenSociety.IDS[role()]);tag.putInt("ElfAppearance",appearance());tag.putLong("ElfLastRestock",lastRestock);tag.putString("ElfTradeRole",ElvenSociety.IDS[role()]);}
    @Override public void readAdditionalSaveData(CompoundTag tag){super.readAdditionalSaveData(tag);entityData.set(ROLE,ElvenSociety.role(tag.getString("ElfRole")));entityData.set(LOOK,Math.floorMod(tag.getInt("ElfAppearance"),4));setAge(0);lastRestock=tag.contains("ElfLastRestock")?tag.getLong("ElfLastRestock"):-1;
        // Spawn eggs merge their role into a default entity save, which already contains offers.
        // Keep saved stock only when it belongs to the restored role.
        if(!tag.getString("ElfTradeRole").equals(ElvenSociety.IDS[role()])){offers=null;lastRestock=-1;}
    }
    @Override public SpawnGroupData finalizeSpawn(ServerLevelAccessor level,DifficultyInstance difficulty,MobSpawnType reason,SpawnGroupData group,CompoundTag tag){
        var result=super.finalizeSpawn(level,difficulty,reason,group,tag);setAge(0);return result;
    }
}

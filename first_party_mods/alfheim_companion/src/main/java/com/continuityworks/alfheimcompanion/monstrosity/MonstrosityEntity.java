package com.continuityworks.alfheimcompanion.monstrosity;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.world.DifficultyInstance;
import net.minecraft.world.effect.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.ai.goal.target.*;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.npc.AbstractVillager;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.*;
import java.util.EnumSet;

/** Nineteen different anatomies and combat timings; three stored habitat appearances each. */
public final class MonstrosityEntity extends Monster {
    private static final EntityDataAccessor<Integer> VARIANT=SynchedEntityData.defineId(MonstrosityEntity.class,EntityDataSerializers.INT);
    public final MonstrosityKind kind;
    private int animationTicks,attackCooldown;
    public MonstrosityEntity(EntityType<? extends Monster> type,Level level,MonstrosityKind kind){super(type,level);this.kind=kind;xpReward=kind==MonstrosityKind.TROLL||kind==MonstrosityKind.CYCLOPS?12:8;}
    @Override public MobType getMobType(){return kind==MonstrosityKind.WENDIGO||kind==MonstrosityKind.BRIDE?MobType.UNDEAD:super.getMobType();}
    @Override protected void defineSynchedData(){super.defineSynchedData();entityData.define(VARIANT,0);}
    public int variant(){return Math.floorMod(entityData.get(VARIANT),3);}
    public static AttributeSupplier.Builder attributes(MonstrosityKind k){return Monster.createMonsterAttributes()
        .add(Attributes.MAX_HEALTH,k.health).add(Attributes.ATTACK_DAMAGE,k.damage).add(Attributes.MOVEMENT_SPEED,k.speed)
        .add(Attributes.ARMOR,k.armor).add(Attributes.FOLLOW_RANGE,28)
        .add(Attributes.KNOCKBACK_RESISTANCE,k==MonstrosityKind.TROLL?.7:k==MonstrosityKind.GARGOYLE?.6:.2);}
    @Override protected void registerGoals(){
        goalSelector.addGoal(0,new FloatGoal(this));
        goalSelector.addGoal(2,new AttackGoal(this));
        goalSelector.addGoal(6,new WaterAvoidingRandomStrollGoal(this,.75));
        goalSelector.addGoal(7,new LookAtPlayerGoal(this,Player.class,10));goalSelector.addGoal(8,new RandomLookAroundGoal(this));
        targetSelector.addGoal(1,new HurtByTargetGoal(this));
        targetSelector.addGoal(2,new NearestAttackableTargetGoal<>(this,Player.class,true));
        targetSelector.addGoal(3,new NearestAttackableTargetGoal<>(this,AbstractVillager.class,true));
    }
    @Override protected net.minecraft.sounds.SoundEvent getAmbientSound(){return kind==null?null:ModMenagerieSounds.get(kind,ModMenagerieSounds.Cue.AMBIENT);}
    @Override protected net.minecraft.sounds.SoundEvent getHurtSound(net.minecraft.world.damagesource.DamageSource source){return ModMenagerieSounds.get(kind,ModMenagerieSounds.Cue.HURT);}
    @Override protected net.minecraft.sounds.SoundEvent getDeathSound(){return ModMenagerieSounds.get(kind,ModMenagerieSounds.Cue.DEATH);}
    @Override public void playAmbientSound(){super.playAmbientSound();if(kind!=null&&random.nextBoolean())playSound(ModMenagerieSounds.get(kind,ModMenagerieSounds.Cue.STEP),.13F,1);}
    @Override public int getAmbientSoundInterval(){return kind!=null&&kind.spawnerOnly()?220:180;}
    @Override protected void playStepSound(net.minecraft.core.BlockPos pos,net.minecraft.world.level.block.state.BlockState state){playSound(ModMenagerieSounds.get(kind,ModMenagerieSounds.Cue.STEP),kind.spawnerOnly()?.14F:.35F,1);}
    @Override public void aiStep(){super.aiStep();if(animationTicks>0)animationTicks--;if(attackCooldown>0)attackCooldown--;}
    /** The command audit simulates entity ticks with a fixed server clock; prime normal goal selection once. */
    void selectAuditGoals(){goalSelector.tick();}
    public float attackMotion(float partial){return animationTicks<=0?0:(float)Math.sin(Math.PI*(1-(animationTicks-partial)/(kind.windup+10F)));}
    private void windUp(){playSound(ModMenagerieSounds.get(kind,ModMenagerieSounds.Cue.WINDUP),.75F,1);animationTicks=kind.windup+10;level().broadcastEntityEvent(this,(byte)4);}
    @Override public void handleEntityEvent(byte event){if(event==4)animationTicks=kind.windup+10;else super.handleEntityEvent(event);}
    /** Recheck distance and sight at impact: no attacks through terrain or while the victim escapes. */
    public boolean strike(LivingEntity target){
        if(level().isClientSide||!target.isAlive()||distanceToSqr(target)>kind.reach*kind.reach||!hasLineOfSight(target))return false;
        var before=MonstrosityDamageState.capture(target);boolean hit;
        if(kind==MonstrosityKind.HAG||kind==MonstrosityKind.BRIDE||kind==MonstrosityKind.PRISM_WARDEN){
            hit=target.hurt(damageSources().indirectMagic(this,this),(float)getAttributeValue(Attributes.ATTACK_DAMAGE));
            ((ServerLevel)level()).sendParticles(kind==MonstrosityKind.PRISM_WARDEN?ParticleTypes.ELECTRIC_SPARK:ParticleTypes.WITCH,target.getX(),target.getY()+.8,target.getZ(),12,.3,.4,.3,.03);
        }else hit=doHurtTarget(target);
        hit=hit||before.wasHarmed(target);
        if(hit){
            playSound(ModMenagerieSounds.get(kind,ModMenagerieSounds.Cue.ATTACK),.8F,1);
            switch(kind){
                case TROLL,CYCLOPS->target.knockback(kind==MonstrosityKind.TROLL?1.1:1.35,getX()-target.getX(),getZ()-target.getZ());
                case BRIAR->target.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,60,0),this);
                case INFESTOR->{target.addEffect(new MobEffectInstance(MobEffects.POISON,60,0),this);target.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,40,0),this);}
                case CRYSTAL_COLOSSUS->{target.knockback(1.3,getX()-target.getX(),getZ()-target.getZ());target.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,60,0),this);}
                case SHARD_REAVER->target.addEffect(new MobEffectInstance(MobEffects.WEAKNESS,40,0),this);
                case PRISM_WARDEN->{target.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,60,0),this);target.addEffect(new MobEffectInstance(MobEffects.DARKNESS,60,0),this);}
                case MARROW_TICK->target.addEffect(new MobEffectInstance(MobEffects.POISON,40,0),this);
                case RIB_BURROWER->target.addEffect(new MobEffectInstance(MobEffects.WEAKNESS,60,0),this);
                case PARASITE_MAW->{target.addEffect(new MobEffectInstance(MobEffects.POISON,60,0),this);target.addEffect(new MobEffectInstance(MobEffects.WEAKNESS,60,0),this);}
                case SINEW_LEECH->{target.addEffect(new MobEffectInstance(MobEffects.WEAKNESS,80,0),this);target.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,40,0),this);heal(1.5F);}
                case WENDIGO->{target.knockback(.85,getX()-target.getX(),getZ()-target.getZ());target.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,80,0),this);target.addEffect(new MobEffectInstance(MobEffects.WEAKNESS,80,0),this);}
                case DUSKWEAVER->{target.addEffect(new MobEffectInstance(MobEffects.POISON,60,0),this);target.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,40,0),this);}
                case BRIDE->{target.addEffect(new MobEffectInstance(MobEffects.DARKNESS,80,0),this);target.addEffect(new MobEffectInstance(MobEffects.WEAKNESS,100,0),this);}
                case MAW->{target.addEffect(new MobEffectInstance(MobEffects.WEAKNESS,60,0),this);target.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,40,0),this);}
                case NUCKELAVEE->{target.knockback(.7,getX()-target.getX(),getZ()-target.getZ());target.addEffect(new MobEffectInstance(MobEffects.WEAKNESS,80,0),this);}
                case HAG->target.addEffect(new MobEffectInstance(MobEffects.POISON,80,0),this);
                default->{}
            }
        }return hit;
    }
    @Override protected Component getTypeName(){return Component.literal(kind.variants[variant()]+" "+kind.label);}
    @Override public SpawnGroupData finalizeSpawn(ServerLevelAccessor level,DifficultyInstance difficulty,MobSpawnType reason,SpawnGroupData group,CompoundTag tag){
        var result=super.finalizeSpawn(level,difficulty,reason,group,tag);
        entityData.set(VARIANT,kind.crystal()?random.nextInt(3):kind.variantFor(level.getBiome(blockPosition()).unwrapKey().map(k->k.location().toString()).orElse("")));return result;
    }
    @Override public void addAdditionalSaveData(CompoundTag tag){super.addAdditionalSaveData(tag);tag.putInt("MonstrosityVariant",variant());tag.putInt("MonstrosityCooldown",attackCooldown);}
    @Override public void readAdditionalSaveData(CompoundTag tag){super.readAdditionalSaveData(tag);entityData.set(VARIANT,Math.floorMod(tag.getInt("MonstrosityVariant"),3));attackCooldown=Math.max(0,Math.min(100,tag.getInt("MonstrosityCooldown")));}
    private static final class AttackGoal extends Goal {
        private final MonstrosityEntity mob;private int windup;
        AttackGoal(MonstrosityEntity mob){this.mob=mob;setFlags(EnumSet.of(Flag.MOVE,Flag.LOOK));}
        @Override public boolean canUse(){return mob.getTarget()!=null&&mob.getTarget().isAlive();}
        @Override public boolean requiresUpdateEveryTick(){return true;}
        @Override public void stop(){windup=0;mob.getNavigation().stop();}
        @Override public void tick(){
            var target=mob.getTarget();if(target==null)return;
            mob.getLookControl().setLookAt(target,30,30);
            double d=mob.distanceToSqr(target);boolean visible=mob.getSensing().hasLineOfSight(target);
            if(!visible||d>mob.kind.reach*mob.kind.reach){windup=0;mob.getNavigation().moveTo(target,1);return;}
            mob.getNavigation().stop();
            if(windup>0){
                if(mob.kind==MonstrosityKind.HAG)((ServerLevel)mob.level()).sendParticles(ParticleTypes.WITCH,mob.getX(),mob.getEyeY(),mob.getZ(),2,.2,.1,.2,0);
                if(--windup==0){mob.strike(target);mob.attackCooldown=mob.kind.cooldown;}return;
            }
            if(mob.attackCooldown==0){
                if((mob.kind==MonstrosityKind.GARGOYLE||mob.kind==MonstrosityKind.DUSKWEAVER||mob.kind==MonstrosityKind.SHARD_REAVER)&&mob.onGround()){
                    var direction=target.position().subtract(mob.position()).normalize();mob.setDeltaMovement(direction.x*.5,.42,direction.z*.5);
                }
                windup=mob.kind.windup;mob.windUp();
            }
        }
    }
}

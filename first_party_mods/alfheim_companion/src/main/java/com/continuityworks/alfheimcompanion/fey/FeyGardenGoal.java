package com.continuityworks.alfheimcompanion.fey;

import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.level.block.CropBlock;
import net.minecraft.world.level.block.SaplingBlock;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.registries.ForgeRegistries;
import java.util.*;

/** Optional wild-pixie routine; normal combat, panic and player-owned behavior retain priority. */
public final class FeyGardenGoal extends Goal {
    private final PathfinderMob mob;private FeyHomeBlockEntity home;private BlockPos target;private boolean returning;private int ticks,linger;
    public FeyGardenGoal(PathfinderMob mob){this.mob=mob;setFlags(EnumSet.of(Flag.MOVE,Flag.LOOK));}
    public static void joined(EntityJoinLevelEvent event){
        if(event.getLevel().isClientSide||!(event.getEntity() instanceof PathfinderMob mob))return;
        var key=ForgeRegistries.ENTITY_TYPES.getKey(mob.getType());if(key==null||!key.getNamespace().equals("feywild"))return;
        if(Arrays.stream(ModFeyHomes.SEASONS).anyMatch(s->key.getPath().equals(s+"_pixie")))mob.goalSelector.addGoal(4,new FeyGardenGoal(mob));
    }
    @Override public boolean canUse(){
        if(mob.tickCount%80!=0||!FeyHomeBlockEntity.freeWild(mob))return false;
        var id=ForgeRegistries.ENTITY_TYPES.getKey(mob.getType());
        home=FeyHomeBlockEntity.nearby(mob.level(),mob.blockPosition(),48).stream().filter(h->h.occupied()<3&&h.entityId().equals(id.toString())).min(Comparator.comparingDouble(h->h.getBlockPos().distSqr(mob.blockPosition()))).orElse(null);
        if(home==null)return false;
        returning=mob.level().isNight()||mob.level().isRaining()||mob.getPersistentData().getInt("FeyVisits")>=3;
        if(returning){if(!mob.level().isNight()&&!mob.level().isRaining()&&mob.level().getGameTime()<mob.getPersistentData().getLong("FeyOutUntil"))return false;target=home.getBlockPos().relative(home.getBlockState().getValue(FeyHomeBlock.FACING));return true;}
        var r=mob.getRandom();
        for(int i=0;i<160;i++){
            var p=home.getBlockPos().offset(r.nextInt(33)-16,r.nextInt(25)-20,r.nextInt(33)-16);
            if(!mob.level().hasChunkAt(p))continue;var state=mob.level().getBlockState(p);
            if((state.is(BlockTags.FLOWERS)||state.getBlock() instanceof CropBlock||state.getBlock() instanceof SaplingBlock)&&mob.level().getBlockState(p.above()).getCollisionShape(mob.level(),p.above()).isEmpty()){
                target=p.above();return true;
            }
        }
        return false;
    }
    @Override public void start(){ticks=0;linger=0;mob.getNavigation().moveTo(target.getX()+.5,target.getY()+.3,target.getZ()+.5,1);}
    @Override public boolean canContinueToUse(){return ticks<240&&mob.isAlive()&&home!=null&&!home.isRemoved()&&mob.getTarget()==null&&FeyHomeBlockEntity.freeWild(mob);}
    @Override public void tick(){
        ticks++;if(ticks%20==0)mob.getNavigation().moveTo(target.getX()+.5,target.getY()+.3,target.getZ()+.5,1);
        mob.getLookControl().setLookAt(target.getX()+.5,target.getY(),target.getZ()+.5);
        if(mob.distanceToSqr(target.getX()+.5,target.getY()+.3,target.getZ()+.5)>2.5)return;
        if(returning){if(home.admit(mob))ticks=240;return;}
        if(++linger<30)return;
        var server=(ServerLevel)mob.level();server.sendParticles(ParticleTypes.HAPPY_VILLAGER,mob.getX(),mob.getY(),mob.getZ(),4,.2,.2,.2,0);
        var data=mob.getPersistentData();data.putInt("FeyVisits",data.getInt("FeyVisits")+1);
        var plant=target.below();var state=server.getBlockState(plant);
        if(state.getBlock() instanceof CropBlock crop&&!crop.isMaxAge(state)&&server.getGameTime()>=data.getLong("FeyGrowAfter")&&net.minecraftforge.event.ForgeEventFactory.getMobGriefingEvent(server,mob)){
            server.setBlockAndUpdate(plant,crop.getStateForAge(crop.getAge(state)+1));data.putLong("FeyGrowAfter",server.getGameTime()+1200);
        }
        ticks=240;
    }
    @Override public void stop(){mob.getNavigation().stop();home=null;target=null;}
}

package com.continuityworks.alfheimcompanion.fey;

import net.minecraft.core.*;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.*;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraftforge.registries.ForgeRegistries;
import java.util.*;

public final class FeyHomeBlockEntity extends BlockEntity {
    private static final Map<Level,Set<BlockPos>> INDEX=Collections.synchronizedMap(new WeakHashMap<>());
    private final List<CompoundTag> residents=new ArrayList<>();
    private boolean nursery=true;
    private long nextBirth=0;
    public FeyHomeBlockEntity(BlockPos p,BlockState s){super(ModFeyHomes.HOME.get(),p,s);}
    public String entityId(){return "feywild:"+((FeyHomeBlock)getBlockState().getBlock()).season+"_pixie";}
    public int occupied(){return residents.size();}
    @Override public void onLoad(){super.onLoad();if(level!=null&&!level.isClientSide)INDEX.computeIfAbsent(level,k->new HashSet<>()).add(worldPosition.immutable());}
    @Override public void setRemoved(){if(level!=null){var set=INDEX.get(level);if(set!=null)set.remove(worldPosition);}super.setRemoved();}
    public static List<FeyHomeBlockEntity> nearby(Level level,BlockPos pos,int range){
        var result=new ArrayList<FeyHomeBlockEntity>();var set=INDEX.get(level);if(set==null)return result;
        for(var p:new ArrayList<>(set))if(p.distSqr(pos)<range*range&&level.hasChunkAt(p)&&level.getBlockEntity(p) instanceof FeyHomeBlockEntity h)result.add(h);
        return result;
    }
    public static boolean freeWild(Mob mob){
        if(mob.isLeashed()||mob.isPassenger()||mob.isVehicle()||mob.getTarget()!=null)return false;
        // Feywild 5.5.5 serializes ownership as Owner. Owned/quest followers stay in the world.
        var data=mob.saveWithoutId(new CompoundTag());return !data.hasUUID("Owner")&&!data.getBoolean("FollowingPlayer");
    }
    public boolean admit(Mob mob){
        if(residents.size()>=3||!freeWild(mob)||!Objects.equals(ForgeRegistries.ENTITY_TYPES.getKey(mob.getType()),new ResourceLocation(entityId()))||mob.distanceToSqr(worldPosition.getX()+.5,worldPosition.getY()+.5,worldPosition.getZ()+.5)>9)return false;
        CompoundTag data=new CompoundTag();if(!mob.save(data))return false;
        var entry=new CompoundTag();entry.put("Entity",data);entry.putLong("ReleaseAt",level.getGameTime()+600+level.random.nextInt(600));residents.add(entry);
        setChanged();mob.discard();return true;
    }
    private boolean release(ServerLevel server,CompoundTag data){
        var facing=getBlockState().getValue(FeyHomeBlock.FACING);
        for(int offset:new int[]{1,2,3}){
            BlockPos exit=worldPosition.relative(facing,offset);
            if(!server.hasChunkAt(exit)||!server.getBlockState(exit).getCollisionShape(server,exit).isEmpty()||!server.getFluidState(exit).isEmpty())continue;
            var entity=EntityType.loadEntityRecursive(data.copy(),server,e->e);if(!(entity instanceof Mob mob))return false;
            mob.moveTo(exit.getX()+.5,exit.getY()+.15,exit.getZ()+.5,0,0);
            if(!server.noCollision(mob,mob.getBoundingBox()))continue;
            mob.getPersistentData().putLong("FeyOutUntil",server.getGameTime()+1200);
            mob.getPersistentData().putInt("FeyVisits",0);
            if(!server.addFreshEntity(mob))return false;
            server.sendParticles(ParticleTypes.HAPPY_VILLAGER,mob.getX(),mob.getY()+.3,mob.getZ(),3,.1,.15,.1,0);return true;
        }
        return false;
    }
    public static void tick(Level level,BlockPos pos,BlockState state,FeyHomeBlockEntity home){
        if(!(level instanceof ServerLevel server)||(level.getGameTime()+pos.asLong())%40!=0)return;
        boolean active=server.hasNearbyAlivePlayer(pos.getX()+.5,pos.getY()+.5,pos.getZ()+.5,24);
        if(!active)return;
        if(level.isDay()&&!level.isRaining())for(int i=0;i<home.residents.size();i++){
            var entry=home.residents.get(i);
            if(level.getGameTime()>=entry.getLong("ReleaseAt")&&home.release(server,entry.getCompound("Entity"))){home.residents.remove(i);home.setChanged();break;}
        }
        if(home.nursery&&level.getGameTime()>=home.nextBirth){
            home.nextBirth=level.getGameTime()+2400+level.random.nextInt(1200);home.setChanged();
            int count=server.getEntitiesOfClass(Mob.class,new AABB(pos).inflate(48),e->Objects.equals(ForgeRegistries.ENTITY_TYPES.getKey(e.getType()),new ResourceLocation(home.entityId()))).size();
            for(var h:nearby(level,pos,48))if(h.entityId().equals(home.entityId()))count+=h.occupied();
            if(count<8&&home.occupied()<3){
                var type=ForgeRegistries.ENTITY_TYPES.getValue(new ResourceLocation(home.entityId()));
                if(type!=null&&type.create(server) instanceof Mob mob){
                    mob.moveTo(pos.getX()+.5,pos.getY()+.5,pos.getZ()+.5,0,0);
                    mob.finalizeSpawn(server,server.getCurrentDifficultyAt(pos),MobSpawnType.SPAWNER,null,null);
                    CompoundTag data=new CompoundTag();if(mob.save(data)){var entry=new CompoundTag();entry.put("Entity",data);entry.putLong("ReleaseAt",level.getGameTime()+200+level.random.nextInt(400));home.residents.add(entry);home.setChanged();}
                }
            }
        }
    }
    @Override protected void saveAdditional(CompoundTag tag){super.saveAdditional(tag);ListTag list=new ListTag();residents.forEach(r->list.add(r.copy()));tag.put("Residents",list);tag.putBoolean("Nursery",nursery);tag.putLong("NextBirth",nextBirth);}
    @Override public void load(CompoundTag tag){super.load(tag);residents.clear();for(var r:tag.getList("Residents",Tag.TAG_COMPOUND)){
        var entry=(CompoundTag)r;String id=entry.getCompound("Entity").getString("id");
        if(residents.size()<3&&id.equals(entityId()))residents.add(entry.copy());
    }nursery=!tag.contains("Nursery")||tag.getBoolean("Nursery");nextBirth=tag.getLong("NextBirth");}
}

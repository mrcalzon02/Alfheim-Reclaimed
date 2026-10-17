package com.continuityworks.alfheimcompanion.monstrosity;

import com.continuityworks.alfheimcompanion.AlfheimCompanion;
import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Blocks;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Opt-in disposable-world proof; this command builds a small stone test floor. */
@Mod.EventBusSubscriber(modid=AlfheimCompanion.MOD_ID)
public final class MonstrosityAudit {
    @SubscribeEvent public static void commands(RegisterCommandsEvent event){
        event.getDispatcher().register(Commands.literal("alfheim_monstrosities_audit").requires(s->s.hasPermission(2)).executes(c->{
            try{
            var source=c.getSource();var level=source.getLevel();var origin=BlockPos.containing(source.getPosition());
            for(int x=-5;x<=5;x++)for(int z=-5;z<=5;z++)level.setBlockAndUpdate(origin.offset(x,-1,z),Blocks.STONE.defaultBlockState());
            var biomes=level.registryAccess().registryOrThrow(Registries.BIOME);int count=0,spawnEntries=0;
            for(var kind:MonstrosityKind.values()){
                var type=ModMonstrosities.TYPES.get(kind).get();
                if(!kind.spawnerOnly()){
                    var tag=TagKey.create(Registries.BIOME,new ResourceLocation("alfheim_companion",kind.id+"_habitats"));
                    var habitats=biomes.getTag(tag).orElseThrow();require(habitats.size()>0,"habitat coverage");
                    for(var biome:habitats){
                        var entries=biome.value().getMobSettings().getMobs(MobCategory.MONSTER).unwrap().stream().filter(e->e.type==type).toList();
                        require(entries.size()==1&&entries.get(0).minCount==1&&entries.get(0).maxCount==1,"one bounded spawn entry");spawnEntries++;
                    }
                    int accepted=0;for(int i=0;i<64;i++)if(SpawnPlacements.checkSpawnRules(type,level,MobSpawnType.NATURAL,origin,RandomSource.create(842+i)))accepted++;
                    require(accepted>0,"natural spawn rule "+kind.id);
                }else{
                    require(!SpawnPlacements.checkSpawnRules(type,level,MobSpawnType.NATURAL,origin,RandomSource.create(842)),"parasites reject natural spawning");
                    require(SpawnPlacements.checkSpawnRules(type,level,MobSpawnType.SPAWNER,origin,RandomSource.create(842)),"corpse spawner rule");
                }
                for(int variant=0;variant<3;variant++){
                    var stack=ItemStack.of(ModMonstrosities.selection(kind,variant).save(new CompoundTag()));
                    require(ModMonstrosities.variant(stack)==variant&&!stack.hasCustomHoverName(),"saved head selection");
                    var mob=type.spawn(level,stack,null,origin,MobSpawnType.SPAWN_EGG,false,false);require(mob!=null,"actual egg spawn");
                    var victim=EntityType.COW.create(level);require(victim!=null,"attack target");
                    try{
                        mob.setNoAi(true);mob.setPos(origin.getX()+.5,origin.getY(),origin.getZ()+.5);
                        require(mob.kind==kind&&mob.variant()==variant,"correct species/variant");
                        require(Math.abs(mob.getBbHeight()-kind.height)<.001,"physical height");
                        if(kind==MonstrosityKind.TROLL)require(Math.abs(mob.getBbHeight()/EntityType.PLAYER.getHeight()-2)<.001,"twice player height");
                        victim.setNoAi(true);victim.setPos(mob.getX(),mob.getY(),mob.getZ()+Math.min(1.7,kind.reach-.15));level.addFreshEntity(victim);
                        // The level advances entity age before ticking; M&S guards newborn targets.
                        for(int tick=0;tick<32;tick++){level.tickNonPassenger(mob);level.tickNonPassenger(victim);}
                        mob.setPos(origin.getX()+.5,origin.getY(),origin.getZ()+.5);mob.setDeltaMovement(0,0,0);
                        victim.setPos(mob.getX(),mob.getY(),mob.getZ()+Math.min(1.7,kind.reach-.15));victim.setDeltaMovement(0,0,0);victim.invulnerableTime=0;
                        victim.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1000);victim.setHealth(1000);
                        var before=MonstrosityDamageState.capture(victim);boolean hit=mob.strike(victim);
                        require(hit&&before.wasHarmed(victim),"attack deals damage "+kind.id+" hit="+hit+" before="+before+" after="+MonstrosityDamageState.capture(victim)+" sight="+mob.hasLineOfSight(victim)+" distance="+mob.distanceTo(victim));
                        if(kind==MonstrosityKind.BRIAR)require(victim.hasEffect(MobEffects.MOVEMENT_SLOWDOWN),"briar slow");
                        if(kind==MonstrosityKind.INFESTOR||kind==MonstrosityKind.HAG)require(victim.hasEffect(MobEffects.POISON),"poison strike");
                        if(kind==MonstrosityKind.WENDIGO||kind==MonstrosityKind.BRIDE||kind==MonstrosityKind.MAW||kind==MonstrosityKind.NUCKELAVEE)require(victim.hasEffect(MobEffects.WEAKNESS),"nightmare weakening strike");
                        if(kind==MonstrosityKind.DUSKWEAVER)require(victim.hasEffect(MobEffects.POISON),"duskweaver venom");
                        if(kind==MonstrosityKind.BRIDE)require(victim.hasEffect(MobEffects.DARKNESS),"bride soul touch");
                        victim.setPos(mob.getX(),mob.getY(),mob.getZ()+Math.min(1.7,kind.reach-.15));victim.invulnerableTime=0;
                        var wall=origin.offset(0,0,1);
                        for(int y=0;y<6;y++)level.setBlockAndUpdate(wall.above(y),Blocks.STONE.defaultBlockState());
                        try{require(!mob.strike(victim),"solid wall blocks attack "+kind.id);}
                        finally{for(int y=0;y<6;y++)level.setBlockAndUpdate(wall.above(y),Blocks.AIR.defaultBlockState());}
                        victim.setPos(mob.getX(),mob.getY(),mob.getZ()+kind.reach+2);require(!mob.strike(victim),"out of reach");
                        if(variant==0){
                            victim.removeAllEffects();victim.invulnerableTime=0;victim.setHealth(1000);
                            victim.setDeltaMovement(0,0,0);victim.setPos(mob.getX(),mob.getY(),mob.getZ()+1.5);
                            mob.setNoAi(false);mob.setTarget(victim);mob.selectAuditGoals();
                            boolean aiDamage=false,aiCooldown=false;
                            // Observe at impact, before passive healing; allow normal combat evasion.
                            for(int tick=0;tick<4*(kind.windup+kind.cooldown+8)&&!(aiDamage&&aiCooldown);tick++){
                                var aiBefore=MonstrosityDamageState.capture(victim);
                                level.tickNonPassenger(mob);aiDamage|=aiBefore.wasHarmed(victim);
                                var aiState=new CompoundTag();mob.addAdditionalSaveData(aiState);aiCooldown|=aiState.getInt("MonstrosityCooldown")>0;
                                level.tickNonPassenger(victim);
                            }
                            require(aiCooldown&&aiDamage,"native AI windup and attack "+kind.id+" cooldown="+aiCooldown+" damage="+aiDamage+" distance="+mob.distanceTo(victim)+" target="+mob.getTarget()+" health="+victim.getHealth());
                            mob.setNoAi(true);mob.setTarget(null);
                        }
                        var saved=new CompoundTag();mob.addAdditionalSaveData(saved);var copy=type.create(level);require(copy!=null,"restore creature");
                        try{copy.readAdditionalSaveData(saved);require(copy.variant()==variant&&copy.kind==kind,"saved variant identity");}finally{if(copy!=null)copy.discard();}
                        require(mob.getLootTable().toString().equals("alfheim_companion:entities/"+kind.id),"dedicated loot table");count++;
                    }finally{if(mob!=null)mob.discard();if(victim!=null)victim.discard();}
                }
            }
            final int passed=count,entries=spawnEntries;source.sendSuccess(()->Component.literal("ALFHEIM_MONSTROSITIES_PASS species="+MonstrosityKind.values().length+" appearances="+passed+" attack_checks="+passed+" sight_blocks="+passed+" saved_variants="+passed+" ai_attacks="+MonstrosityKind.values().length+" habitat_entries="+entries+" troll_player_height_ratio=2.0"),false);return count;
            }catch(Exception failure){AlfheimCompanion.LOGGER.error("Monstrosity runtime audit failed",failure);throw failure;}
        }));
    }
    private static void require(boolean value,String message){if(!value)throw new IllegalStateException("Monstrosity audit: "+message);}
    private MonstrosityAudit(){}
}

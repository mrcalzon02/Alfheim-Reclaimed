package com.continuityworks.alfheimcompanion.society;

import com.continuityworks.alfheimcompanion.AlfheimCompanion;
import com.continuityworks.alfheimcompanion.registry.ModEntities;
import net.minecraft.commands.Commands;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Explicit disposable-world probe: creates, validates and immediately discards 48 citizens. */
@Mod.EventBusSubscriber(modid=AlfheimCompanion.MOD_ID)
public final class ElvenSocietyAudit {
    @SubscribeEvent public static void commands(RegisterCommandsEvent event){
        event.getDispatcher().register(Commands.literal("alfheim_society_audit").requires(s->s.hasPermission(2)).executes(c->{
            var level=c.getSource().getLevel();var pos=net.minecraft.core.BlockPos.containing(c.getSource().getPosition());int count=0;
            for(int role=0;role<12;role++)for(int look=0;look<4;look++){
                var stack=ElvenSociety.selection(role,look);stack=ItemStack.of(stack.save(new CompoundTag()));
                if(ElvenSociety.modelKey(stack)!=role*4+look+1||stack.hasCustomHoverName())throw new IllegalStateException("Citizen item selection mismatch");
                var elf=ModEntities.ELVEN_CITIZEN.get().spawn(level,stack,null,pos,MobSpawnType.SPAWN_EGG,false,false);
                if(elf==null)throw new IllegalStateException("Citizen spawn rejected");
                try{
                    if(elf.role()!=role||elf.appearance()!=look||elf.hasCustomName()||elf.removeWhenFarAway(100000))throw new IllegalStateException("Citizen appearance/persistence mismatch");
                    CompoundTag saved=new CompoundTag();elf.addAdditionalSaveData(saved);
                    var copy=ModEntities.ELVEN_CITIZEN.get().create(level);
                    if(copy==null)throw new IllegalStateException("Citizen restoration rejected");
                    copy.readAdditionalSaveData(saved);
                    if(copy.role()!=role||copy.appearance()!=look||copy.getTarget()!=null)throw new IllegalStateException("Citizen saved appearance/peaceful target mismatch");
                    copy.discard();
                }finally{elf.discard();}count++;
            }
            final int passed=count;c.getSource().sendSuccess(()->Component.literal("ALFHEIM_SOCIETY_PASS roles=12 appearances="+passed+" actual_egg_spawns="+passed+" saved_npc_roundtrips="+passed),false);return count;
        }));
    }
    private ElvenSocietyAudit(){}
}

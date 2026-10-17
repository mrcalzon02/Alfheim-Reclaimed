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
        event.getDispatcher().register(Commands.literal("alfheim_society_trade_audit").requires(s->s.hasPermission(2)).executes(c->auditTrades(c.getSource())));
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
    private static int auditTrades(net.minecraft.commands.CommandSourceStack source){
        var level=source.getLevel();var pos=net.minecraft.core.BlockPos.containing(source.getPosition());
        var player=net.minecraftforge.common.util.FakePlayerFactory.getMinecraft(level);int transactions=0;
        for(int role=0;role<12;role++)for(int look=0;look<4;look++){
            var elf=ModEntities.ELVEN_CITIZEN.get().spawn(level,ElvenSociety.selection(role,look),null,pos,MobSpawnType.SPAWN_EGG,false,false);
            if(elf==null)throw new IllegalStateException("Trader spawn rejected");
            try{
                var offers=elf.getOffers();require(offers.size()==6,"six offers per role");
                require(offers.createTag().equals(ElvenCitizenTrades.offers(role).createTag()),"spawn egg selects correct role catalogue");
                elf.setTradingPlayer(player);
                var menu=new net.minecraft.world.inventory.MerchantMenu(91,player.getInventory(),elf);
                require(menu.stillValid(player),"trading customer owns menu");
                for(int i=0;i<offers.size();i++){
                    var offer=offers.get(i);menu.getSlot(0).set(ItemStack.EMPTY);menu.getSlot(1).set(ItemStack.EMPTY);
                    menu.setSelectionHint(i);menu.getSlot(0).set(offer.getCostA().copy());
                    require(menu.getSlot(2).getItem().isEmpty(),"second payment required");
                    var shortPayment=offer.getCostB().copy();shortPayment.shrink(1);menu.getSlot(1).set(shortPayment);
                    require(menu.getSlot(2).getItem().isEmpty(),"insufficient second payment rejected");
                    menu.getSlot(1).set(offer.getCostB().copy());
                    require(ItemStack.matches(menu.getSlot(2).getItem(),offer.getResult()),"native menu output");
                    var taken=menu.getSlot(2).remove(offer.getResult().getCount());menu.getSlot(2).onTake(player,taken);
                    require(ItemStack.matches(taken,offer.getResult()),"correct trade result");
                    require(menu.getSlot(0).getItem().isEmpty()&&menu.getSlot(1).getItem().isEmpty(),"both payments consumed");
                    require(offer.getUses()==1,"stock consumed once");transactions++;
                }
                menu.removed(player);require(!elf.isTrading(),"customer released on close");
                var first=offers.get(0);first.setToOutOfStock();
                elf.setTradingPlayer(player);menu=new net.minecraft.world.inventory.MerchantMenu(92,player.getInventory(),elf);
                menu.setSelectionHint(0);menu.getSlot(0).set(first.getCostA().copy());menu.getSlot(1).set(first.getCostB().copy());
                require(menu.getSlot(2).getItem().isEmpty(),"exhausted stock blocks output");
                // Clear audit inputs before closing; they were never taken from a real player's inventory.
                menu.getSlot(0).set(ItemStack.EMPTY);menu.getSlot(1).set(ItemStack.EMPTY);menu.removed(player);
                var saved=new CompoundTag();elf.addAdditionalSaveData(saved);
                var copy=ModEntities.ELVEN_CITIZEN.get().create(level);require(copy!=null,"restore trader");
                try{
                    copy.readAdditionalSaveData(saved);
                    require(copy.role()==role&&copy.appearance()==look&&!copy.isBaby(),"adult identity survives save");
                    require(copy.getOffers().createTag().equals(offers.createTag()),"offers and stock survive save");
                    require(!copy.restockAt(level.getGameTime()+ElvenCitizenTrades.restockTicks()-1),"early restock rejected after save");
                    require(copy.restockAt(level.getGameTime()+ElvenCitizenTrades.restockTicks()),"daily restock");
                    require(copy.getOffers().stream().allMatch(o->o.getUses()==0),"all stock restored");
                    require(!copy.restockAt(level.getGameTime()+ElvenCitizenTrades.restockTicks()),"no repeated refresh");
                }finally{if(copy!=null)copy.discard();}
            }finally{elf.setTradingPlayer(null);elf.discard();}
        }
        final int passed=transactions;source.sendSuccess(()->Component.literal("ALFHEIM_ELVEN_TRADES_PASS citizens=48 catalogue=72 menu_transactions="+passed+" persisted_stock=48 daily_restocks=48"),false);return transactions;
    }
    private static void require(boolean condition,String message){if(!condition)throw new IllegalStateException("Elf trade audit: "+message);}
    private ElvenSocietyAudit(){}
}

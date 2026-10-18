package com.continuityworks.alfheimcompanion.society;

import com.continuityworks.alfheimcompanion.AlfheimCompanion;
import com.continuityworks.alfheimcompanion.registry.ModEntities;
import com.continuityworks.alfheimcompanion.worldgen.MonasteryLabyrinthPiece;
import com.continuityworks.alfheimcompanion.worldgen.ActOneAuthoredInteriors;
import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.*;
import net.minecraft.world.inventory.MerchantMenu;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.phys.AABB;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Explicit disposable-world test. Never called by ordinary world generation. */
@Mod.EventBusSubscriber(modid=AlfheimCompanion.MOD_ID)
public final class ActOneRefugeAudit {
    @SubscribeEvent public static void commands(RegisterCommandsEvent event){
        event.getDispatcher().register(Commands.literal("alfheim_refuge_audit").requires(s->s.hasPermission(2))
            .executes(c->audit(c.getSource())));
    }
    private static int audit(net.minecraft.commands.CommandSourceStack source){
        var level=source.getLevel();var at=BlockPos.containing(source.getPosition());
        var bounds=new BoundingBox(at.getX(),at.getY(),at.getZ(),at.getX()+64,at.getY()+21,at.getZ()+72);
        require(level.getEntitiesOfClass(ElvenCitizenEntity.class,AABB.of(bounds)).isEmpty(),"use a fresh disposable test site");
        var village=new MonasteryLabyrinthPiece("village",1,0,0,at.getX(),at.getY(),at.getZ(),65,22,73);
        for(int x=bounds.minX()>>4;x<=bounds.maxX()>>4;x++)for(int z=bounds.minZ()>>4;z<=bounds.maxZ()>>4;z++){
            level.getChunk(x,z);
            village.postProcess(level,level.structureManager(),level.getChunkSource().getGenerator(),level.random,
                new BoundingBox(x*16,level.getMinBuildHeight(),z*16,x*16+15,level.getMaxBuildHeight()-1,z*16+15),new ChunkPos(x,z),at);
        }
        var vendors=level.getEntitiesOfClass(ElvenCitizenEntity.class,AABB.of(bounds));require(vendors.size()==6,"exactly six template merchants across chunk boundaries");
        var services=new java.util.HashSet<String>();var player=net.minecraftforge.common.util.FakePlayerFactory.getMinecraft(level);
        int transactions=0;
        try{
            player.getInventory().clearContent();
            for(var vendor:vendors){
                vendor.setNoAi(true);require(services.add(vendor.refugeService()),"one merchant per service");
                require(vendor.isPersistenceRequired()&&vendor.getTarget()==null,"persistent passive merchant");
                var offers=vendor.getOffers();require(!offers.isEmpty(),"non-empty stock");
                vendor.setTradingPlayer(player);var menu=new MerchantMenu(95,player.getInventory(),vendor);
                for(int i=0;i<offers.size();i++){
                    var offer=offers.get(i);menu.getSlot(0).set(ItemStack.EMPTY);menu.getSlot(1).set(ItemStack.EMPTY);menu.setSelectionHint(i);
                    menu.getSlot(0).set(offer.getCostA().copy());require(menu.getSlot(2).getItem().isEmpty(),"both payments required");
                    var shortPay=offer.getCostB().copy();shortPay.shrink(1);menu.getSlot(1).set(shortPay);
                    require(menu.getSlot(2).getItem().isEmpty(),"short payment rejected");
                    menu.getSlot(1).set(offer.getCostB().copy());require(ItemStack.matches(menu.getSlot(2).getItem(),offer.getResult()),"native merchant result");
                    var output=menu.getSlot(2).remove(offer.getResult().getCount());menu.getSlot(2).onTake(player,output);
                    require(ItemStack.matches(output,offer.getResult()),"correct bought stack");
                    require(menu.getSlot(0).getItem().isEmpty()&&menu.getSlot(1).getItem().isEmpty()&&offer.getUses()==1,"exact consumption and stock");
                    if(vendor.refugeService().equals("arms")){
                        var gear=com.robertx22.mine_and_slash.uncommon.datasaving.StackSaving.GEARS.loadFrom(output);
                        require(gear!=null&&gear.isValidItem()&&gear.getLevel()==1&&gear.getRarityId().equals("common"),"native common level-one MMO stats");
                    }
                    transactions++;
                }
                menu.removed(player);offers.get(0).setToOutOfStock();
                var saved=new CompoundTag();vendor.addAdditionalSaveData(saved);var copy=ModEntities.ELVEN_CITIZEN.get().create(level);
                require(copy!=null,"merchant restore");
                try{
                    copy.readAdditionalSaveData(saved);require(copy.refugeService().equals(vendor.refugeService()),"service persists");
                    require(copy.getOffers().createTag().equals(offers.createTag()),"rolled gear and used stock persist");
                    require(!copy.restockAt(level.getGameTime()+23999),"no early restock");require(copy.restockAt(level.getGameTime()+24000),"daily restock");
                    require(!copy.restockAt(level.getGameTime()+24000),"no repeated restock");
                }finally{copy.discard();}
            }
            require(services.equals(java.util.Set.of(ActOneAuthoredInteriors.SERVICES)),"all six services");
            var weapon=ActOneRefugeTrades.offers("arms").get(0).getResult().copy();weapon.setDamageValue(101);
            weapon.getOrCreateTag().putString("AuditIdentity","keep_me");weapon.enchant(net.minecraft.world.item.enchantment.Enchantments.UNBREAKING,2);
            var expected=weapon.copy();expected.setDamageValue(0);player.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND,weapon);
            require(!ActOneRefugeTrades.repair(player)&&weapon.getDamageValue()==101,"unpaid repair rejected");
            var a=net.minecraftforge.registries.ForgeRegistries.ITEMS.getValue(new net.minecraft.resources.ResourceLocation("botania:manasteel_ingot"));
            var b=net.minecraftforge.registries.ForgeRegistries.ITEMS.getValue(new net.minecraft.resources.ResourceLocation("ars_nouveau:source_gem"));
            player.getInventory().setItem(9,new ItemStack(a,3));player.getInventory().setItem(10,new ItemStack(b,1));
            require(!ActOneRefugeTrades.repair(player)&&player.getInventory().getItem(9).getCount()==3,"partial payment is atomic");
            player.getInventory().setItem(10,new ItemStack(b,3));require(ActOneRefugeTrades.repair(player),"paid repair");
            require(ItemStack.matches(weapon,expected),"all MMO, identity and enchantment NBT preserved except Damage");
            require(player.getInventory().getItem(9).getCount()==1&&player.getInventory().getItem(10).getCount()==1,"repair price rounds up by durability");
            require(!ActOneRefugeTrades.repair(player)&&player.getInventory().getItem(9).getCount()==1,"no charge for undamaged gear");
        }finally{player.getInventory().clearContent();for(var vendor:vendors)vendor.setTradingPlayer(null);}
        // Exercise a furnished room whose north-only boundary must stay closed on three sides.
        var roomAt=at.offset(80,0,0);var roomBounds=new BoundingBox(roomAt.getX(),roomAt.getY(),roomAt.getZ(),roomAt.getX()+28,roomAt.getY()+14,roomAt.getZ()+28);
        var room=new MonasteryLabyrinthPiece("room",1,1,5,roomAt.getX(),roomAt.getY(),roomAt.getZ(),29,15,29);
        room.postProcess(level,level.structureManager(),level.getChunkSource().getGenerator(),level.random,roomBounds,new ChunkPos(roomAt),roomAt);
        require(level.getBlockState(roomAt.offset(14,2,0)).isAir(),"open graph door");
        for(var p:java.util.List.of(roomAt.offset(14,2,28),roomAt.offset(0,2,14),roomAt.offset(28,2,14)))require(!level.getBlockState(p).isAir(),"closed graph doors preserved");
        final int n=transactions;source.sendSuccess(()->Component.literal("ALFHEIM_REFUGE_PASS vendors=6 offers="+n+" persisted_stock=6 restocks=6 repairs=paid_atomic_nbt_preserved dungeon_doors=preserved"),false);return n;
    }
    private static void require(boolean value,String message){if(!value)throw new IllegalStateException("Refuge audit: "+message);}
    private ActOneRefugeAudit(){}
}

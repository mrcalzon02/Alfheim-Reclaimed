package com.continuityworks.alfheimcompanion.society;

import com.google.gson.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.*;
import net.minecraft.world.item.alchemy.*;
import net.minecraft.world.item.trading.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.network.chat.Component;
import net.minecraftforge.registries.ForgeRegistries;
import com.robertx22.mine_and_slash.loot.LootInfo;
import com.robertx22.mine_and_slash.loot.blueprints.GearBlueprint;
import com.robertx22.mine_and_slash.uncommon.datasaving.StackSaving;
import com.robertx22.mine_and_slash.database.data.profession.LeveledItem;

/** Native MMO stacks and paid, NBT-preserving repairs. No replacement currency or equipment system. */
public final class ActOneRefugeTrades {
    private static final JsonObject DATA=load();
    private static JsonObject load(){
        try(var stream=ActOneRefugeTrades.class.getResourceAsStream("/data/alfheim_companion/act_one_refuge_trades.json")){
            if(stream==null)throw new IllegalStateException("Missing refuge stock");
            return JsonParser.parseReader(new InputStreamReader(stream,StandardCharsets.UTF_8)).getAsJsonObject();
        }catch(IOException e){throw new IllegalStateException(e);}
    }
    public static boolean known(String service){return DATA.getAsJsonObject("services").has(service);}
    public static long restockTicks(){return DATA.get("restock_ticks").getAsLong();}
    private static Item item(String id){
        var key=new ResourceLocation(id);
        if(!ForgeRegistries.ITEMS.containsKey(key))throw new IllegalStateException("Missing refuge item "+id);
        var item=ForgeRegistries.ITEMS.getValue(key);
        if(item==null||item==Items.AIR)throw new IllegalStateException("Invalid refuge item "+id);
        return item;
    }
    private static ItemStack stack(JsonObject row,String key,String count){
        var result=new ItemStack(item(row.get(key).getAsString()),row.get(count).getAsInt());
        if(result.getCount()<1||result.getCount()>result.getMaxStackSize())throw new IllegalStateException("Invalid refuge stack");
        return result;
    }
    public static MerchantOffers offers(String service){
        if(!known(service))throw new IllegalArgumentException("Unknown refuge service");
        var result=new MerchantOffers();
        for(var value:DATA.getAsJsonObject("services").getAsJsonArray(service)){
            var row=value.getAsJsonObject();var output=stack(row,"result","count");
            if(row.has("gear_type")){
                var bp=new GearBlueprint(LootInfo.ofLevel(row.get("gear_level").getAsInt()));
                bp.level.set(row.get("gear_level").getAsInt());
                bp.setType(row.get("gear_type").getAsString());
                bp.rarity.canRollUnique=false;bp.rarity.canRollRuned=false;bp.rarity.chanceForHigherRarity=0;
                bp.rarity.set(com.robertx22.mine_and_slash.database.registry.ExileDB.GearRarities().get(row.get("gear_rarity").getAsString()));
                output=bp.createStack();
                var gear=StackSaving.GEARS.loadFrom(output);
                if(output.isEmpty()||gear==null||!gear.isValidItem()||gear.getLevel()!=1||!gear.getRarityId().equals("common"))
                    throw new IllegalStateException("Refuge gear generation failed");
            }else if(row.has("potion")){
                var id=new ResourceLocation(row.get("potion").getAsString());
                if(!ForgeRegistries.POTIONS.containsKey(id))throw new IllegalStateException("Missing potion "+id);
                PotionUtils.setPotion(output,ForgeRegistries.POTIONS.getValue(id));
            }
            if(row.has("tier"))LeveledItem.setTier(output,row.get("tier").getAsInt());
            result.add(new MerchantOffer(stack(row,"cost_a","count_a"),stack(row,"cost_b","count_b"),output,
                row.get("max_uses").getAsInt(),0,0F));
        }
        return result;
    }
    public static int repairPrice(ItemStack held){return held.isDamageableItem()&&held.isDamaged()?(held.getDamageValue()+99)/100:0;}
    /** Called on the server main thread after merchant/customer ownership checks. */
    public static boolean repair(Player player){
        var held=player.getMainHandItem();int price=repairPrice(held);
        if(price==0){player.displayClientMessage(Component.literal("Hold a damaged weapon, armor piece or tool to repair it."),false);return false;}
        var a=item(DATA.getAsJsonObject("repair").get("cost_a").getAsString());
        var b=item(DATA.getAsJsonObject("repair").get("cost_b").getAsString());
        if(count(player,a)<price||count(player,b)<price){
            player.displayClientMessage(Component.literal("Full repair costs "+price+" Manasteel Ingots and "+price+" Source Gems. Keep them in your inventory, then crouch and interact again."),false);return false;
        }
        consume(player,a,price);consume(player,b,price);held.setDamageValue(0);
        player.getInventory().setChanged();player.containerMenu.broadcastChanges();
        player.displayClientMessage(Component.literal("Repaired for "+price+" Manasteel Ingots and "+price+" Source Gems. Enchantments and equipment stats preserved."),false);return true;
    }
    private static int count(Player player,Item item){return player.getInventory().items.stream().filter(s->s.is(item)&&!s.hasTag()).mapToInt(ItemStack::getCount).sum();}
    private static void consume(Player player,Item item,int count){
        for(var stack:player.getInventory().items)if(stack.is(item)&&!stack.hasTag()){
            int used=Math.min(count,stack.getCount());stack.shrink(used);count-=used;if(count==0)return;
        }
        throw new IllegalStateException("Repair payment changed during transaction");
    }
    private ActOneRefugeTrades(){}
}

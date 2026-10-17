package com.continuityworks.alfheimcompanion.society;

import com.google.gson.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.*;
import net.minecraft.world.item.trading.*;
import net.minecraftforge.registries.ForgeRegistries;

/** Authored barter catalogue. Never substitute air for a missing pack ingredient. */
public final class ElvenCitizenTrades {
    private static final JsonObject CATALOGUE=load();
    private static JsonObject load(){
        try(var stream=ElvenCitizenTrades.class.getResourceAsStream("/data/alfheim_companion/elven_trades.json")){
            if(stream==null)throw new IllegalStateException("Missing elf trade catalogue");
            return JsonParser.parseReader(new InputStreamReader(stream,StandardCharsets.UTF_8)).getAsJsonObject();
        }catch(IOException e){throw new IllegalStateException("Cannot read elf trades",e);}
    }
    public static long restockTicks(){return CATALOGUE.get("restock_ticks").getAsLong();}
    private static ItemStack stack(JsonObject row,String key,String countKey){
        var id=new ResourceLocation(row.get(key).getAsString());
        if(!ForgeRegistries.ITEMS.containsKey(id))throw new IllegalStateException("Missing elf trade item "+id);
        var item=ForgeRegistries.ITEMS.getValue(id);int count=row.get(countKey).getAsInt();
        if(item==null||item==Items.AIR||count<1||count>item.getMaxStackSize())throw new IllegalStateException("Invalid elf trade stack "+id);
        return new ItemStack(item,count);
    }
    public static MerchantOffers offers(int role){
        var result=new MerchantOffers();
        for(var value:CATALOGUE.getAsJsonObject("roles").getAsJsonArray(ElvenSociety.IDS[ElvenSociety.safeRole(role)])){
            var row=value.getAsJsonObject();
            var offer=new MerchantOffer(stack(row,"cost_a","count_a"),stack(row,"cost_b","count_b"),
                stack(row,"result","count"),row.get("max_uses").getAsInt(),0,0F);
            result.add(offer);
        }
        return result;
    }
    private ElvenCitizenTrades(){}
}

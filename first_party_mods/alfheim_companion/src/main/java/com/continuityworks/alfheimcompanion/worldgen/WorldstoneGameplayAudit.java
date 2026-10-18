package com.continuityworks.alfheimcompanion.worldgen;

import com.continuityworks.alfheimcompanion.AlfheimCompanion;
import com.continuityworks.alfheimcompanion.worldstone.*;
import com.google.gson.*;
import com.mojang.brigadier.arguments.IntegerArgumentType;
import net.minecraft.commands.Commands;
import net.minecraft.core.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.item.*;
import net.minecraft.world.item.enchantment.Enchantments;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;
import java.util.*;

/** Explicit operator probe for disposable worlds; restores its single growth fixture. */
@Mod.EventBusSubscriber(modid=AlfheimCompanion.MOD_ID)
public final class WorldstoneGameplayAudit {
    @SubscribeEvent public static void register(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("alfheim_worldstone_gameplay").requires(s->s.hasPermission(2))
            .then(Commands.argument("x",IntegerArgumentType.integer()).then(Commands.argument("z",IntegerArgumentType.integer()).executes(c->{
                var level=c.getSource().getLevel();
                if(!level.dimension().location().toString().equals("mythicbotany:alfheim"))return 0;
                var result=run(level,IntegerArgumentType.getInteger(c,"x"),IntegerArgumentType.getInteger(c,"z"));
                c.getSource().sendSuccess(()->Component.literal("WORLDSTONE_GAMEPLAY "+result),false);return 1;
            }))));
    }
    private static void require(boolean condition,String message){if(!condition)throw new IllegalStateException(message);}
    private static JsonArray drops(ServerLevel level,BlockPos pos,BlockState state,ItemStack tool) {
        var result=new JsonArray();
        for(var stack:Block.getDrops(state,level,pos,null,null,tool)) {
            var item=new JsonObject();item.addProperty("item",ForgeRegistries.ITEMS.getKey(stack.getItem()).toString());item.addProperty("count",stack.getCount());result.add(item);
        }
        return result;
    }
    public static JsonObject run(ServerLevel level,int x,int z) {
        var result=new JsonObject();result.addProperty("x",x);result.addProperty("z",z);
        BlockPos bud=null,source=null;Direction direction=null;
        outer:for(int dx=-60;dx<=60;dx++)for(int y=-8;y<=140;y++)for(int dz=-60;dz<=60;dz++) {
            int face=WorldstoneLayout.seedFace(dx,y,dz);if(face<0)continue;
            var at=new BlockPos(x+dx,y,z+dz);var state=level.getBlockState(at);
            if(!state.is(ModWorldstoneBlocks.CLUSTER.get()))continue;
            direction=state.getValue(AmethystClusterBlock.FACING);source=at.relative(direction.getOpposite());
            if(level.getBlockState(source).is(ModWorldstoneBlocks.CRYSTAL.get())){bud=at;break outer;}
        }
        require(bud!=null,"No naturally seeded Worldstone cluster found");
        var original=level.getBlockState(bud);var pick=new ItemStack(Items.DIAMOND_PICKAXE);
        var normal=drops(level,bud,original,pick);
        require(normal.size()==1 && normal.get(0).getAsJsonObject().get("item").getAsString().equals("alfheim_companion:worldstone_fragment")
            && normal.get(0).getAsJsonObject().get("count").getAsInt()==4,"Mature cluster must drop four fragments");
        var silk=new ItemStack(Items.DIAMOND_PICKAXE);silk.enchant(Enchantments.SILK_TOUCH,1);
        var fortune=new ItemStack(Items.DIAMOND_PICKAXE);fortune.enchant(Enchantments.BLOCK_FORTUNE,3);
        result.add("mature_drops",normal);result.add("mature_fortune_drops",drops(level,bud,original,fortune));
        var silkDrops=drops(level,bud,original,silk);require(silkDrops.size()==1 && silkDrops.get(0).getAsJsonObject().get("item").getAsString().equals("alfheim_companion:worldstone_cluster"),"Cluster Silk Touch");
        require(drops(level,source,level.getBlockState(source),silk).isEmpty(),"Budding sources must not relocate through Silk Touch");
        var stages=new JsonArray();
        try {
            level.setBlockAndUpdate(bud,Blocks.CAVE_AIR.defaultBlockState());
            for(var expected:List.of(ModWorldstoneBlocks.SMALL,ModWorldstoneBlocks.MEDIUM,ModWorldstoneBlocks.LARGE,ModWorldstoneBlocks.CLUSTER)) {
                require(WorldstoneBuddingBlock.grow(level,source,direction),"Worldstone growth stalled");
                require(level.getBlockState(bud).is(expected.get()),"Wrong Worldstone growth stage");
                stages.add(ForgeRegistries.BLOCKS.getKey(expected.get()).toString());
            }
            require(!WorldstoneBuddingBlock.grow(level,source,direction),"Mature cluster must stop growing");
            level.setBlockAndUpdate(bud,Blocks.CAVE_AIR.defaultBlockState());
            require(WorldstoneBuddingBlock.grow(level,source,direction) && level.getBlockState(bud).is(ModWorldstoneBlocks.SMALL.get()),"Harvested cluster did not regrow");
        } finally {level.setBlockAndUpdate(bud,original);}
        result.add("growth_stages",stages);result.addProperty("harvest_regrowth",true);result.addProperty("budding_silk_touch_drops",0);
        BlockPos ore=null;
        outer:for(int dx=-118;dx<=118;dx+=2)for(int dz=-118;dz<=118;dz+=2)for(int y=-40;y<80;y+=2) {
            if(!WorldstoneLayout.ore(dx,y,dz))continue;double q=WorldstoneLayout.density(dx,y,dz);if(q<1 || q>1.065)continue;
            var at=new BlockPos(x+dx,y,z+dz);if(level.getBlockState(at).is(ModWorldstoneBlocks.ORE.get())){ore=at;break outer;}
        }
        require(ore!=null,"No naturally generated fragment ore");
        var oreDrops=drops(level,ore,level.getBlockState(ore),pick);
        require(oreDrops.size()==1 && oreDrops.get(0).getAsJsonObject().get("item").getAsString().equals("alfheim_companion:worldstone_fragment"),"Ore did not produce fragments");
        result.add("ore_drops",oreDrops);result.add("ore_fortune_drops",drops(level,ore,level.getBlockState(ore),fortune));
        var compass=new ItemStack(ModWorldstoneBlocks.COMPASS.get());var task=new WorldstoneNavigation.Task(level,new BlockPos(x-320,80,z),compass);
        long begin=System.nanoTime();while(!task.complete && System.nanoTime()-begin<5_000_000_000L)task.step(16);
        require(task.complete && task.target!=null && task.target.equals(new BlockPos(x,60,z)),"Compass did not find the actual natural Worldstone");
        var reloaded=ItemStack.of(compass.save(new CompoundTag()));var global=CompassItem.getLodestonePosition(reloaded.getOrCreateTag());
        require(global!=null && global.pos().equals(task.target) && global.dimension().equals(level.dimension()),"Compass target did not survive serialization");
        require(!reloaded.getOrCreateTag().getBoolean("LodestoneTracked"),"Compass must not require a vanilla Lodestone block");
        require(reloaded.getDescriptionId().equals("item.alfheim_companion.worldstone_compass"),"Bound compass lost its Worldstone name");
        result.addProperty("compass_tested_candidates",task.tested());result.addProperty("compass_target_saved",true);result.addProperty("compass_nbt",reloaded.getOrCreateTag().toString());
        var recipes=new JsonArray();
        for(String id:List.of("worldstone_compass","attuned_worldstone","divine_ore","godly_ore","legendary_stone","mythic_stone")) {
            var key=new ResourceLocation("alfheim","worldstone/"+id);var recipe=level.getRecipeManager().byKey(key).orElseThrow(()->new IllegalStateException("Missing native recipe "+key));
            var output=recipe.getResultItem(level.registryAccess());require(!output.isEmpty(),"Empty Worldstone recipe output "+key);
            var row=new JsonObject();row.addProperty("id",key.toString());row.addProperty("output",ForgeRegistries.ITEMS.getKey(output.getItem()).toString());row.addProperty("count",output.getCount());recipes.add(row);
        }
        result.add("native_recipes",recipes);return result;
    }
    private WorldstoneGameplayAudit(){}
}

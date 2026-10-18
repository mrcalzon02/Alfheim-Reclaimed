package com.continuityworks.alfheimcompanion.worldgen;

import com.continuityworks.alfheimcompanion.AlfheimCompanion;
import com.google.gson.*;
import com.mojang.brigadier.arguments.IntegerArgumentType;
import net.minecraft.commands.Commands;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.entity.RandomizableContainerBlockEntity;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.placement.RandomSpreadStructurePlacement;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.*;

/** Bounded operator-only survey and actual container-opening probe for disposable worlds. */
@Mod.EventBusSubscriber(modid=AlfheimCompanion.MOD_ID)
public final class FairyIslandAudit {
    @SubscribeEvent public static void register(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("alfheim_fairy_islands_audit").requires(s->s.hasPermission(2))
            .then(Commands.argument("regionX",IntegerArgumentType.integer(-100,100)).then(Commands.argument("regionZ",IntegerArgumentType.integer(-100,100)).executes(c->{
                var source=c.getSource();var level=source.getLevel();
                if(!level.dimension().location().toString().equals("mythicbotany:alfheim"))return 0;
                int rx=IntegerArgumentType.getInteger(c,"regionX"),rz=IntegerArgumentType.getInteger(c,"regionZ"),tested=0,accepted=0;
                var registry=level.registryAccess().registryOrThrow(Registries.STRUCTURE);
                var sets=level.registryAccess().registryOrThrow(Registries.STRUCTURE_SET);
                var generator=level.getChunkSource().getGenerator();var reasons=new TreeMap<String,Integer>();long start=System.nanoTime();
                for(int i=0;i<64;i++) {
                    if(i>0 && System.nanoTime()-start>5_000_000_000L)break;
                    var sample=sets.get(new ResourceLocation("alfheim","pixie_spring_hamlet"));
                    var placement=(RandomSpreadStructurePlacement)sample.placement();
                    var chunk=placement.getPotentialStructureChunk(level.getSeed(),(rx+i%8)*96,(rz+i/8)*96);tested++;
                    String reason="outside_seasonal_biomes";
                    for(String season:new String[]{"spring","summer","autumn","winter"}) {
                        var id=new ResourceLocation("alfheim","pixie_"+season+"_hamlet");
                        var structure=(FeySkyVillageStructure)registry.get(id);
                        var biome=generator.getBiomeSource().getNoiseBiome(chunk.getMiddleBlockX()>>2,16,chunk.getMiddleBlockZ()>>2,level.getChunkSource().randomState().sampler());
                        if(!structure.biomes().contains(biome))continue;
                        var context=new Structure.GenerationContext(level.registryAccess(),generator,generator.getBiomeSource(),level.getChunkSource().randomState(),level.getStructureManager(),level.getSeed(),chunk,level,structure.biomes()::contains);
                        reason=structure.rejection(context);
                        if(reason.equals("none") && structure.findValidGenerationPoint(context).isPresent()) {
                            accepted++;String message="FAIRY_SITE season="+season+" x="+chunk.getMinBlockX()+" z="+chunk.getMinBlockZ();
                            source.sendSuccess(()->Component.literal(message),false);
                        } else if(reason.equals("none"))reason="anchor_biome";
                        break;
                    }
                    reasons.merge(reason,1,Integer::sum);
                }
                String message="FAIRY_SURVEY region="+rx+","+rz+" tested="+tested+" accepted="+accepted+" reasons="+reasons;
                source.sendSuccess(()->Component.literal(message),false);return accepted;
            }))));
        event.getDispatcher().register(Commands.literal("alfheim_fairy_islands_loot").requires(s->s.hasPermission(2))
            .then(Commands.argument("x",IntegerArgumentType.integer()).then(Commands.argument("z",IntegerArgumentType.integer()).executes(c->{
                var source=c.getSource();var level=source.getLevel();int x=IntegerArgumentType.getInteger(c,"x"),z=IntegerArgumentType.getInteger(c,"z");
                var result=new JsonObject();result.addProperty("x",x);result.addProperty("z",z);var containers=new JsonArray();
                for(int cx=x/16-3;cx<=x/16+3;cx++)for(int cz=z/16-3;cz<=z/16+3;cz++)
                    for(var entity:level.getChunk(cx,cz).getBlockEntities().values()) {
                        var pos=entity.getBlockPos();
                        if(pos.getY()<192 || pos.getY()>=240 || !(entity instanceof RandomizableContainerBlockEntity barrel))continue;
                        var before=barrel.saveWithFullMetadata();
                        if(!before.getString("LootTable").startsWith("alfheim:chests/fairy_island_"))continue;
                        var row=new JsonObject();row.addProperty("x",pos.getX());row.addProperty("y",pos.getY());row.addProperty("z",pos.getZ());
                        row.addProperty("table",before.getString("LootTable"));row.addProperty("seed",before.getLong("LootTableSeed"));
                        barrel.unpackLootTable(null);var items=new JsonArray();
                        for(int slot=0;slot<barrel.getContainerSize();slot++) {
                            var stack=barrel.getItem(slot);if(stack.isEmpty())continue;
                            var item=new JsonObject();item.addProperty("slot",slot);item.addProperty("item",net.minecraftforge.registries.ForgeRegistries.ITEMS.getKey(stack.getItem()).toString());item.addProperty("count",stack.getCount());items.add(item);
                        }
                        if(items.isEmpty() || barrel.saveWithFullMetadata().contains("LootTable"))throw new IllegalStateException("Fairy loot was not unpacked");
                        String saved=barrel.saveWithFullMetadata().toString();barrel.getItem(0);
                        if(!saved.equals(barrel.saveWithFullMetadata().toString()))throw new IllegalStateException("Loot rerolled on repeated access");
                        barrel.setChanged();row.add("items",items);containers.add(row);
                    }
                if(containers.size()<10)throw new IllegalStateException("Expected at least ten natural island loot containers, got "+containers.size());
                result.add("containers",containers);source.sendSuccess(()->Component.literal("FAIRY_LOOT_RESULT "+result),false);return containers.size();
            }))));
    }
}

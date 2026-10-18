package com.continuityworks.alfheimcompanion.worldgen;

import com.continuityworks.alfheimcompanion.AlfheimCompanion;
import com.mojang.brigadier.arguments.IntegerArgumentType;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.placement.RandomSpreadStructurePlacement;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.TreeMap;

/** Operator-only bounded noise survey; never changes terrain or loads chunks. */
@Mod.EventBusSubscriber(modid=AlfheimCompanion.MOD_ID)
public final class WorldstoneCommands {
    @SubscribeEvent public static void register(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("alfheim_worldstone_mountains").requires(s->s.hasPermission(2))
            .then(Commands.argument("regionX",IntegerArgumentType.integer(-100,100))
            .then(Commands.argument("regionZ",IntegerArgumentType.integer(-100,100)).executes(c->{
                var source=c.getSource();var level=source.getLevel();
                if(!level.dimension().location().toString().equals("mythicbotany:alfheim"))return 0;
                int rx=IntegerArgumentType.getInteger(c,"regionX"),rz=IntegerArgumentType.getInteger(c,"regionZ");
                var generator=level.getChunkSource().getGenerator();var state=level.getChunkSource().randomState();
                var histogram=new TreeMap<Integer,Integer>();int tested=0,max=-64;long begin=System.nanoTime();
                for(int i=0;i<256;i++) {
                    if(i>0 && System.nanoTime()-begin>4_000_000_000L)break;
                    int x=rx*2048+(i%16)*128+8,z=rz*2048+(i/16)*128+8;
                    int y=generator.getBaseHeight(x,z,Heightmap.Types.OCEAN_FLOOR_WG,level,state);tested++;
                    histogram.merge(Math.floorDiv(y,16)*16,1,Integer::sum);max=Math.max(max,y);
                    if(y>=180) {
                        var biome=generator.getBiomeSource().getNoiseBiome(x>>2,16,z>>2,state.sampler());
                        String row="WORLDSTONE_PEAK x="+x+" z="+z+" y="+y+" biome="+biome.unwrapKey().map(k->k.location().toString()).orElse("unknown");
                        source.sendSuccess(()->Component.literal(row),false);
                    }
                }
                String row="WORLDSTONE_MOUNTAINS region="+rx+","+rz+" tested="+tested+" max="+max+" histogram="+histogram;
                source.sendSuccess(()->Component.literal(row),false);return tested;
            }))));
        event.getDispatcher().register(Commands.literal("alfheim_worldstone_audit").requires(s->s.hasPermission(2))
            .then(Commands.argument("regionX",IntegerArgumentType.integer(-100,100))
            .then(Commands.argument("regionZ",IntegerArgumentType.integer(-100,100)).executes(c->{
                var source=c.getSource();var level=source.getLevel();
                if(!level.dimension().location().toString().equals("mythicbotany:alfheim"))return 0;
                int rx=IntegerArgumentType.getInteger(c,"regionX"),rz=IntegerArgumentType.getInteger(c,"regionZ"),tested=0,accepted=0;
                var structure=(WorldstoneCavernStructure)level.registryAccess().registryOrThrow(Registries.STRUCTURE).get(WorldstoneCavernStructure.ID);
                var set=level.registryAccess().registryOrThrow(Registries.STRUCTURE_SET).get(WorldstoneCavernStructure.ID);
                if(structure==null || set==null || !(set.placement() instanceof RandomSpreadStructurePlacement placement))return 0;
                var generator=level.getChunkSource().getGenerator();var reasons=new TreeMap<String,Integer>();long begin=System.nanoTime();
                for(int i=0;i<64;i++) {
                    if(i>0 && System.nanoTime()-begin>5_000_000_000L)break;
                    var p=placement.getPotentialStructureChunk(level.getSeed(),(rx+i%8)*placement.spacing(),(rz+i/8)*placement.spacing());
                    var context=new Structure.GenerationContext(level.registryAccess(),generator,generator.getBiomeSource(),
                        level.getChunkSource().randomState(),level.getStructureManager(),level.getSeed(),p,level,structure.biomes()::contains);
                    String reason=structure.rejection(context);tested++;reasons.merge(reason,1,Integer::sum);
                    if(!reason.equals("none") || structure.findValidGenerationPoint(context).isEmpty())continue;
                    accepted++;var probe=structure.site(context);
                    String row="WORLDSTONE_SITE x="+p.getMiddleBlockX()+" z="+p.getMiddleBlockZ()+" summit="+probe.summit()+" cover="+probe.minimumCover();
                    source.sendSuccess(()->Component.literal(row),false);
                }
                String row="WORLDSTONE_AUDIT region="+rx+","+rz+" tested="+tested+" accepted="+accepted+" reasons="+reasons;
                source.sendSuccess(()->Component.literal(row),false);return accepted;
            }))));
    }
}

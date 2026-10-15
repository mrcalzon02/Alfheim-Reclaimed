package com.continuityworks.alfheimcompanion.worldgen;

import com.continuityworks.alfheimcompanion.AlfheimCompanion;
import com.mojang.brigadier.arguments.IntegerArgumentType;
import net.minecraft.commands.Commands;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.placement.RandomSpreadStructurePlacement;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.TreeMap;

/** Operator-only, finite candidate audit. Noise queries only: no chunk loads or writes. */
@Mod.EventBusSubscriber(modid=AlfheimCompanion.MOD_ID)
public final class UpperUnderworldCommands {
    @SubscribeEvent public static void register(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("alfheimupper").requires(s->s.hasPermission(2))
            .then(Commands.literal("audit").then(Commands.argument("regionX",IntegerArgumentType.integer(-1000,1000))
                .then(Commands.argument("regionZ",IntegerArgumentType.integer(-1000,1000))
                    .then(Commands.argument("count",IntegerArgumentType.integer(1,64)).executes(c->{
                        var source=c.getSource();var level=source.getLevel();
                        if(!level.dimension().location().toString().equals("mythicbotany:alfheim")) {
                            source.sendFailure(Component.literal("Upper audit requires Alfheim"));return 0;
                        }
                        var id=new ResourceLocation("alfheim","upper_underworld");
                        var structure=level.registryAccess().registryOrThrow(Registries.STRUCTURE).get(id);
                        var set=level.registryAccess().registryOrThrow(Registries.STRUCTURE_SET).get(id);
                        if(!(structure instanceof UpperUnderworldStructure) || set==null
                            || !(set.placement() instanceof RandomSpreadStructurePlacement placement))return 0;
                        int rx=IntegerArgumentType.getInteger(c,"regionX"),rz=IntegerArgumentType.getInteger(c,"regionZ");
                        int count=IntegerArgumentType.getInteger(c,"count"),tested=0,accepted=0;
                        long begin=System.nanoTime();var reasons=new TreeMap<String,Integer>();
                        var generator=level.getChunkSource().getGenerator();
                        // Explicit maximum of 64 candidates and 2 seconds between candidates.
                        // A single vanilla base-column query cannot be interrupted safely.
                        for(int i=0;i<count;i++) {
                            if(i>0 && System.nanoTime()-begin>2_000_000_000L)break;
                            var chunk=placement.getPotentialStructureChunk(level.getSeed(),(rx+i%8)*placement.spacing(),(rz+i/8)*placement.spacing());
                            var context=new Structure.GenerationContext(level.registryAccess(),generator,generator.getBiomeSource(),
                                level.getChunkSource().randomState(),level.getStructureManager(),level.getSeed(),chunk,level,structure.biomes()::contains);
                            String reason=UpperUnderworldStructure.reservation(context);tested++;
                            if(reason.equals("none")) {
                                // Calls the same biome and terrain predicate as natural worldgen.
                                var stub=structure.findValidGenerationPoint(context);
                                if(stub.isPresent()) {
                                    accepted++;var p=stub.get().position();
                                    source.sendSuccess(()->Component.literal("Upper candidate x="+p.getX()+" y="+p.getY()+" z="+p.getZ()+" chunk="+chunk.x+","+chunk.z),false);
                                    reason="accepted";
                                } else reason="terrain_or_biome";
                            }
                            reasons.merge(reason,1,Integer::sum);
                        }
                        String result="Upper audit seed="+level.getSeed()+" region="+rx+","+rz+" tested="+tested+" accepted="+accepted
                            +" ms="+(System.nanoTime()-begin)/1_000_000+" reasons="+reasons;
                        source.sendSuccess(()->Component.literal(result),false);return accepted;
                    }))))));
    }
}

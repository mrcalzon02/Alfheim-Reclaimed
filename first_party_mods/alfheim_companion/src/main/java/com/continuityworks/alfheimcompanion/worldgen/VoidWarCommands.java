package com.continuityworks.alfheimcompanion.worldgen;
import com.continuityworks.alfheimcompanion.AlfheimCompanion;
import com.mojang.brigadier.arguments.IntegerArgumentType;
import net.minecraft.commands.Commands;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.TreeMap;
@Mod.EventBusSubscriber(modid=AlfheimCompanion.MOD_ID)
public final class VoidWarCommands {
    @SubscribeEvent public static void register(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("alfheimwar").requires(s->s.hasPermission(2))
            .then(Commands.literal("materials").executes(c->{
                var ids=BuiltInRegistries.BLOCK.keySet().stream().filter(id->id.getNamespace().equals("alfheim")
                    && (id.getPath().startsWith("bio_sludge_") || id.getPath().startsWith("titan_")
                    || id.getPath().startsWith("golem_") || id.getPath().startsWith("war_"))).sorted().toList();
                c.getSource().sendSuccess(()->Component.literal("War registry ids="+ids),false);return ids.size();
            }))
            .then(Commands.literal("audit").then(Commands.argument("regionX",IntegerArgumentType.integer(-1000,1000))
                .then(Commands.argument("regionZ",IntegerArgumentType.integer(-1000,1000))
                    .then(Commands.argument("count",IntegerArgumentType.integer(1,64)).executes(c->{
                        var level=c.getSource().getLevel();
                        if(!level.dimension().location().toString().equals("mythicbotany:alfheim"))return 0;
                        var structure=level.registryAccess().registryOrThrow(Registries.STRUCTURE).get(new ResourceLocation("alfheim","last_bulwark"));
                        if(structure==null)return 0;
                        int rx=IntegerArgumentType.getInteger(c,"regionX"),rz=IntegerArgumentType.getInteger(c,"regionZ"),count=IntegerArgumentType.getInteger(c,"count");
                        long begin=System.nanoTime();int tested=0,accepted=0;var reasons=new TreeMap<String,Integer>();
                        var generator=level.getChunkSource().getGenerator();
                        for(int i=0;i<count;i++) {
                            if(i>0 && System.nanoTime()-begin>2_000_000_000L)break;
                            var p=VoidWarPolicy.GRID.getPotentialStructureChunk(level.getSeed(),(rx+i%8)*192,(rz+i/8)*192);
                            var context=new Structure.GenerationContext(level.registryAccess(),generator,generator.getBiomeSource(),level.getChunkSource().randomState(),
                                level.getStructureManager(),level.getSeed(),p,level,structure.biomes()::contains);
                            int winner=VoidWarPolicy.winner(context);
                            var probe=VoidWarStructure.probe(context,winner);String profile=winner<6?"large":"compact";
                            tested++;reasons.merge(probe.reason(),1,Integer::sum);
                            if(probe.accepted()) {
                                accepted++;String message="War candidate chunk="+p.x+","+p.z+" origin="+probe.x()+","+probe.y()+","+probe.z()
                                    +" profile="+profile+" columns="+probe.columns()+" biome_queries="+probe.biomeQueries();
                                c.getSource().sendSuccess(()->Component.literal(message),false);
                            }
                        }
                        String message="War audit region="+rx+","+rz+" tested="+tested+" accepted="+accepted+" ms="+(System.nanoTime()-begin)/1_000_000+" reasons="+reasons;
                        c.getSource().sendSuccess(()->Component.literal(message),false);return accepted;
                    }))))));
    }
}

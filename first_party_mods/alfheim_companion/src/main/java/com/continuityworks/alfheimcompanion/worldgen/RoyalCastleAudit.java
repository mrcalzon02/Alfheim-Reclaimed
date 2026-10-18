package com.continuityworks.alfheimcompanion.worldgen;

import com.continuityworks.alfheimcompanion.AlfheimCompanion;
import net.minecraft.commands.Commands;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.placement.ConcentricRingsStructurePlacement;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Read-only operator diagnostics for the three reserved castle candidates. */
@Mod.EventBusSubscriber(modid=AlfheimCompanion.MOD_ID)
public final class RoyalCastleAudit {
    @SubscribeEvent public static void register(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("alfheim_castle_audit").requires(s->s.hasPermission(2)).executes(c->{
            var source=c.getSource();var level=source.getLevel();
            if(!level.dimension().location().toString().equals("mythicbotany:alfheim"))return 0;
            var id=new ResourceLocation("alfheim","royal_castle");
            var structure=level.registryAccess().registryOrThrow(Registries.STRUCTURE).get(id);
            var set=level.registryAccess().registryOrThrow(Registries.STRUCTURE_SET).get(id);
            if(structure==null || set==null || !(set.placement() instanceof ConcentricRingsStructurePlacement placement))
                throw new IllegalStateException("Missing castle registration");
            var generator=level.getChunkSource().getGenerator();
            var state=level.getChunkSource().randomState();int accepted=0,index=0;
            for(var chunk:level.getChunkSource().getGeneratorState().getRingPositionsFor(placement)) {
                int x=chunk.getMinBlockX(),z=chunk.getMinBlockZ(),low=Integer.MAX_VALUE,high=Integer.MIN_VALUE;
                for(int dx:new int[]{-117,0,117})for(int dz:new int[]{-117,0,117}) {
                    int y=generator.getBaseHeight(x+dx,z+dz,Heightmap.Types.OCEAN_FLOOR_WG,level,state);
                    low=Math.min(low,y);high=Math.max(high,y);
                }
                high=Math.max(high,generator.getSeaLevel()+1);
                var biome=generator.getBiomeSource().getNoiseBiome(x>>2,high>>2,z>>2,state.sampler());
                var context=new Structure.GenerationContext(level.registryAccess(),generator,generator.getBiomeSource(),
                    state,level.getStructureManager(),level.getSeed(),chunk,level,structure.biomes()::contains);
                boolean viable=structure.findValidGenerationPoint(context).isPresent();if(viable)accepted++;
                String result="CASTLE_CANDIDATE index="+(index++)+" x="+x+" z="+z+" low="+low+" high="+high+
                    " sea="+generator.getSeaLevel()+" biome="+biome.unwrapKey().map(k->k.location().toString()).orElse("unknown")+
                    " biome_allowed="+structure.biomes().contains(biome)+" viable="+viable;
                source.sendSuccess(()->Component.literal(result),false);
            }
            final int found=accepted;
            source.sendSuccess(()->Component.literal("CASTLE_AUDIT accepted="+found),false);
            return accepted;
        }));
    }
}

package com.continuityworks.alfheimcompanion.worldgen;

import com.continuityworks.alfheimcompanion.AlfheimCompanion;
import net.minecraft.commands.Commands;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.material.MapColor;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

/** Explicit, bounded operator probe: twelve native sites, no chunk loads or placement. */
@Mod.EventBusSubscriber(modid=AlfheimCompanion.MOD_ID)
public final class DistrictRingAudit {
    @SubscribeEvent public static void register(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("alfheim_district_rings_audit").requires(s->s.hasPermission(2)).executes(c->{
            var source=c.getSource();var level=source.getLevel();
            if(!level.dimension().location().toString().equals("mythicbotany:alfheim"))return 0;
            var generator=level.getChunkSource().getGenerator();int accepted=0;
            for(int ring=1;ring<=3;ring++)for(int slot=0;slot<4;slot++) {
                var site=DistrictRings.site(level.getSeed(),ring,slot);
                var id=new ResourceLocation("alfheim",DistrictPolicy.FAMILIES.get(site.family()));
                var structure=level.registryAccess().registryOrThrow(Registries.STRUCTURE).get(id);
                var set=level.registryAccess().registryOrThrow(Registries.STRUCTURE_SET).get(id);
                if(structure==null || set==null || !(set.placement() instanceof DistrictRingPlacement))
                    throw new IllegalStateException("Missing district ring registration: "+id);
                var chunk=new ChunkPos(site.chunkX(),site.chunkZ());
                var context=new Structure.GenerationContext(level.registryAccess(),generator,generator.getBiomeSource(),
                    level.getChunkSource().randomState(),level.getStructureManager(),level.getSeed(),chunk,level,structure.biomes()::contains);
                boolean viable=structure.findValidGenerationPoint(context).isPresent();if(viable)accepted++;
                String result="DISTRICT_RING_SITE ring="+ring+" slot="+slot+" family="+id+" x="+chunk.getMinBlockX()+" z="+chunk.getMinBlockZ()+" viable="+viable;
                source.sendSuccess(()->Component.literal(result),false);
            }
            int colors=0;
            for(String tree:new String[]{"emberbark","gloambark","hushbark"})for(String suffix:new String[]{"log","leaves","sapling"}) {
                var block=ForgeRegistries.BLOCKS.getValue(new ResourceLocation("alfheim",tree+"_"+suffix));
                if(block==null || block.defaultBlockState().getMapColor(level,level.getSharedSpawnPos())==MapColor.NONE)
                    throw new IllegalStateException("Missing grove map color: "+tree+"_"+suffix);
                colors++;
            }
            final int found=accepted,checked=colors;
            source.sendSuccess(()->Component.literal("DISTRICT_RING_AUDIT_PASS accepted="+found+" grove_map_colors="+checked),false);
            return accepted;
        }));
    }
}

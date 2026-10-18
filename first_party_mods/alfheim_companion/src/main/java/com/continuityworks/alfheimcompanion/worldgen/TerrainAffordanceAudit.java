package com.continuityworks.alfheimcompanion.worldgen;

import com.continuityworks.alfheimcompanion.AlfheimCompanion;
import net.minecraft.commands.Commands;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Runtime coverage gate against the actual loaded registry, including newly added structures. */
@Mod.EventBusSubscriber(modid=AlfheimCompanion.MOD_ID)
public final class TerrainAffordanceAudit {
    @SubscribeEvent public static void register(RegisterCommandsEvent event){
        event.getDispatcher().register(Commands.literal("alfheim_terrain_audit").requires(s->s.hasPermission(2)).executes(c->{
            var registry=c.getSource().registryAccess().registryOrThrow(Registries.STRUCTURE);
            int total=0,grounded=0;
            for(var entry:registry.entrySet()){
                var id=entry.getKey().location();if(!id.getNamespace().equals("alfheim"))continue;
                var p=TerrainAffordances.profiles().get(id);
                if(p==null)throw new IllegalStateException("No terrain contract for "+id);
                if(!BuiltInRegistries.BLOCK.containsKey(new ResourceLocation(p.material())))throw new IllegalStateException("Invalid foundation block for "+id);
                if(p.mode().equals("grounded")){
                    var s=entry.getValue();
                    if(!(s instanceof RemoteDistrictStructure||s instanceof FairyReservedJigsawStructure
                            ||s instanceof VoidWarNeighborStructure||s instanceof AllocatedUndergroundStructure))
                        throw new IllegalStateException("Ground plate adapter missing for "+id);
                    grounded++;
                }
                total++;
            }
            final String result="TERRAIN_AFFORDANCE_AUDIT_PASS structures="+total+" grounded="+grounded;
            c.getSource().sendSuccess(()->Component.literal(result),false);return total;
        }));
    }
}

package com.continuityworks.alfheimcompanion;

import com.continuityworks.alfheimcompanion.brain.CompanionBrainCoordinator;
import com.continuityworks.alfheimcompanion.entity.ElvenCompanionEntity;
import com.continuityworks.alfheimcompanion.memory.CompanionSavedData;
import com.continuityworks.alfheimcompanion.memory.MemoryEntry;
import net.minecraft.server.level.ServerLevel;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.event.server.ServerStoppingEvent;
import com.continuityworks.alfheimcompanion.service.CompanionChunkTickets;
import com.continuityworks.alfheimcompanion.service.CompanionSummonService;
import com.continuityworks.alfheimcompanion.service.QuestMemoryService;
import net.minecraftforge.event.ServerChatEvent;
import com.continuityworks.alfheimcompanion.command.CompanionCommandService;
import com.continuityworks.alfheimcompanion.service.BlueprintLifecycleService;
import com.continuityworks.alfheimcompanion.service.WheelActionService;
import net.minecraftforge.event.RegisterCommandsEvent;
import com.continuityworks.alfheimcompanion.command.CompanionAdminCommands;
import com.continuityworks.alfheimcompanion.service.CompanionDeathInventoryService;
import com.continuityworks.alfheimcompanion.service.BaseOperationsService;

public final class CompanionEvents {
    private CompanionEvents() {}

    @SubscribeEvent
    public static void onServerChat(ServerChatEvent event) {
        if (CompanionCommandService.handle(event.getPlayer(), event.getRawText())) event.setCanceled(true);
    }

    @SubscribeEvent
    public static void onRegisterCommands(RegisterCommandsEvent event) {
        CompanionAdminCommands.register(event.getDispatcher());
    }

    @SubscribeEvent
    public static void onEntityJoin(EntityJoinLevelEvent event) {
        if (!(event.getLevel() instanceof ServerLevel level)
                || !(event.getEntity() instanceof ElvenCompanionEntity companion)) return;

        CompanionSavedData data = CompanionSavedData.get(level.getServer());
        // The sigil service binds an owner before insertion. Reject commands, spawn eggs, other
        // mods, or corrupted NBT attempting to create an unowned companion outside that path.
        if (companion.ownerUuid() == null) {
            AlfheimCompanion.LOGGER.warn("Rejected unbound elven companion {}", companion.getUUID());
            event.setCanceled(true);
            return;
        }
        if (data.companionUuid().isPresent() && !data.companionUuid().get().equals(companion.getUUID())) {
            AlfheimCompanion.LOGGER.warn("Rejected duplicate elven companion {}", companion.getUUID());
            event.setCanceled(true);
            return;
        }

        if (data.companionUuid().isEmpty()) {
            data.bind(companion.getUUID(), companion.ownerUuid(),
                    level.dimension().location().toString(), companion.blockPosition());
        }
    }

    @SubscribeEvent
    public static void onCompanionDeath(LivingDeathEvent event) {
        if (!(event.getEntity() instanceof ElvenCompanionEntity companion)
                || companion.getServer() == null) return;
        CompanionSavedData data = CompanionSavedData.get(companion.getServer());
        CompanionDeathInventoryService.handle(companion, data);
        data.remember(new MemoryEntry(companion.level().getGameTime(), "death", "self",
                event.getSource().getMsgId(), 10));
        data.markCurrentBindingDead();
        BlueprintLifecycleService.cancel(companion.getServer());
        data.dismiss();
        CompanionChunkTickets.release(companion.getUUID());
        CompanionBrainCoordinator.deactivate();
        CompanionBrainCoordinator.clear(companion.getUUID());
    }

    @SubscribeEvent
    public static void onServerTick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END) return;
        CompanionBrainCoordinator.tick(event.getServer());
        BlueprintLifecycleService.tick(event.getServer());
        BaseOperationsService.tick(event.getServer());
        if (event.getServer().getTickCount() % 20 == 0) {
            CompanionSavedData leaseData = CompanionSavedData.get(event.getServer());
            if (leaseData.expireLease(event.getServer().overworld().getGameTime())) {
                BlueprintLifecycleService.cancel(event.getServer());
                CompanionBrainCoordinator.deactivate();
                ElvenCompanionEntity leased = CompanionSummonService.findLoaded(event.getServer(),
                        leaseData.companionUuid().orElse(null));
                if (leased != null) {
                    leased.getNavigation().stop();
                    leased.setMode(com.continuityworks.alfheimcompanion.memory.CompanionMode.WAITING);
                }
            }
        }
        if (event.getServer().getTickCount() % 1200 == 0) {
            CompanionSavedData data = CompanionSavedData.get(event.getServer());
            ElvenCompanionEntity companion = CompanionSummonService.findLoaded(event.getServer(),
                    data.companionUuid().orElse(null));
            if (companion != null && companion.resolveOwner() != null) {
                QuestMemoryService.refresh(companion.resolveOwner(), data);
            }
        }
    }

    @SubscribeEvent
    public static void onServerStopping(ServerStoppingEvent event) {
        CompanionBrainCoordinator.deactivate();
        BlueprintLifecycleService.cancel(event.getServer());
        WheelActionService.clearRateLimits();
        CompanionChunkTickets.releaseAll(event.getServer());
    }
}

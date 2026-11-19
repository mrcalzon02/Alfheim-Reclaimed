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
import com.continuityworks.alfheimcompanion.service.DelegatedClaimService;
import com.continuityworks.alfheimcompanion.service.AutonomousActivityService;

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
        // Allow committed UUID/owner pairs for ordinary reload and cross-world moves.
        // A new UUID must hold a transient admission reservation from the summon service;
        // never persist an unverified UUID just to pass this event.
        if (companion.ownerUuid() == null) {
            AlfheimCompanion.LOGGER.warn("Rejected unbound elven companion {}", companion.getUUID());
            event.setCanceled(true);
            return;
        }
        if (!data.allowsCompanionJoin(companion.getUUID(), companion.ownerUuid())) {
            AlfheimCompanion.LOGGER.warn("Rejected uncommitted or mismatched elven companion {}",
                    companion.getUUID());
            event.setCanceled(true);
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
        DelegatedClaimService.tick(event.getServer());
        AutonomousActivityService.tick(event.getServer());
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
        DelegatedClaimService.clearRuntime();
        AutonomousActivityService.clearRuntime();
        CompanionChunkTickets.releaseAll(event.getServer());
    }
}

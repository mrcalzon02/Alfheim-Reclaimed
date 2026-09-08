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

public final class CompanionEvents {
    private CompanionEvents() {}

    @SubscribeEvent
    public static void onServerChat(ServerChatEvent event) {
        if (CompanionCommandService.handle(event.getPlayer(), event.getRawText())) event.setCanceled(true);
    }

    @SubscribeEvent
    public static void onEntityJoin(EntityJoinLevelEvent event) {
        if (!(event.getLevel() instanceof ServerLevel level)
                || !(event.getEntity() instanceof ElvenCompanionEntity companion)) return;

        CompanionSavedData data = CompanionSavedData.get(level.getServer());
        if (data.companionUuid().isPresent() && !data.companionUuid().get().equals(companion.getUUID())) {
            AlfheimCompanion.LOGGER.warn("Rejected duplicate elven companion {}", companion.getUUID());
            event.setCanceled(true);
            return;
        }

        if (data.companionUuid().isEmpty() && companion.ownerUuid() != null) {
            data.bind(companion.getUUID(), companion.ownerUuid(),
                    level.dimension().location().toString(), companion.blockPosition());
        }
    }

    @SubscribeEvent
    public static void onCompanionDeath(LivingDeathEvent event) {
        if (!(event.getEntity() instanceof ElvenCompanionEntity companion)
                || companion.getServer() == null) return;
        CompanionSavedData data = CompanionSavedData.get(companion.getServer());
        data.remember(new MemoryEntry(companion.level().getGameTime(), "death", "self",
                event.getSource().getMsgId(), 10));
        data.dismiss();
        CompanionChunkTickets.release(companion.getUUID());
        CompanionBrainCoordinator.deactivate();
        CompanionBrainCoordinator.clear(companion.getUUID());
    }

    @SubscribeEvent
    public static void onServerTick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END) return;
        CompanionBrainCoordinator.tick(event.getServer());
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
        CompanionChunkTickets.releaseAll(event.getServer());
    }
}

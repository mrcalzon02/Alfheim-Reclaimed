package com.continuityworks.alfheimcompanion.service;

import com.continuityworks.alfheimcompanion.AlfheimCompanion;
import com.continuityworks.alfheimcompanion.entity.ElvenCompanionEntity;
import com.continuityworks.alfheimcompanion.memory.CompanionSavedData;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.ChunkPos;
import net.minecraftforge.common.world.ForgeChunkManager;

import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.ArrayList;

/** Maintains a bounded 3x3 ticking ticket around the one active companion. */
public final class CompanionChunkTickets {
    private static final int RADIUS = 1;
    private static final Map<UUID, TicketState> ACTIVE = new ConcurrentHashMap<>();

    private CompanionChunkTickets() {}

    public static void registerValidationCallback() {
        ForgeChunkManager.setForcedChunkLoadingCallback(AlfheimCompanion.MOD_ID, (level, helper) -> {
            CompanionSavedData data = CompanionSavedData.get(level.getServer());
            UUID expected = data.mode() == com.continuityworks.alfheimcompanion.memory.CompanionMode.DISMISSED
                    ? null : data.companionUuid().orElse(null);
            for (UUID ticketOwner : new ArrayList<>(helper.getEntityTickets().keySet())) {
                if (!ticketOwner.equals(expected)) helper.removeAllTickets(ticketOwner);
            }
        });
    }

    public static void update(ElvenCompanionEntity companion) {
        if (!(companion.level() instanceof ServerLevel level)) return;
        ChunkPos center = companion.chunkPosition();
        TicketState existing = ACTIVE.get(companion.getUUID());
        if (existing != null && existing.level() == level && existing.center().equals(center)) return;

        force(level, companion.getUUID(), center, true);
        if (existing != null) force(existing.level(), companion.getUUID(), existing.center(), false);
        ACTIVE.put(companion.getUUID(), new TicketState(level, center));
    }

    public static void release(UUID companionUuid) {
        TicketState existing = ACTIVE.remove(companionUuid);
        if (existing != null) force(existing.level(), companionUuid, existing.center(), false);
    }

    public static void releaseAll(MinecraftServer server) {
        for (UUID id : ListCopy.ids()) release(id);
    }

    private static void force(ServerLevel level, UUID owner, ChunkPos center, boolean add) {
        for (int dx = -RADIUS; dx <= RADIUS; dx++) {
            for (int dz = -RADIUS; dz <= RADIUS; dz++) {
                ForgeChunkManager.forceChunk(level, AlfheimCompanion.MOD_ID, owner,
                        center.x + dx, center.z + dz, add, true);
            }
        }
    }

    private record TicketState(ServerLevel level, ChunkPos center) {}

    private static final class ListCopy {
        private static UUID[] ids() { return ACTIVE.keySet().toArray(UUID[]::new); }
    }
}

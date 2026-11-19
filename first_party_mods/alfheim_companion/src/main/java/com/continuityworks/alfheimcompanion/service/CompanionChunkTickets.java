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

        UUID owner = companion.getUUID();
        if (existing == null) {
            force(level, owner, center, true);
        } else if (existing.level() != level) {
            // Different worlds have independent ticket maps; establish destination first.
            force(level, owner, center, true);
            force(existing.level(), owner, existing.center(), false);
        } else {
            // Keep overlap untouched; only acquire entering edges and release outgoing ones.
            for (ChunkTicketDelta.Change change : ChunkTicketDelta.moving(
                    existing.center().x, existing.center().z, center.x, center.z, RADIUS)) {
                ForgeChunkManager.forceChunk(level, AlfheimCompanion.MOD_ID, owner,
                        change.x(), change.z(), change.add(), true);
            }
        }
        ACTIVE.put(owner, new TicketState(level, center));
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

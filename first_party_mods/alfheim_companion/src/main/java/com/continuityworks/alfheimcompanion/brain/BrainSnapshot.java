package com.continuityworks.alfheimcompanion.brain;

import net.minecraft.core.BlockPos;

import java.util.List;
import java.util.Map;
import java.util.UUID;

public record BrainSnapshot(
        long requestId,
        long gameTime,
        UUID companionUuid,
        UUID ownerUuid,
        String dimensionId,
        BlockPos companionPosition,
        BlockPos ownerPosition,
        int ownerHealthPercent,
        List<Threat> threats,
        String activeTask,
        String personality,
        String combatProfile,
        Map<String, String> recalledFacts
) {
    public BrainSnapshot {
        threats = List.copyOf(threats).subList(0, Math.min(3, threats.size()));
        recalledFacts = Map.copyOf(recalledFacts);
    }

    public record Threat(int entityId, String entityType, int distanceSquared) {}
}

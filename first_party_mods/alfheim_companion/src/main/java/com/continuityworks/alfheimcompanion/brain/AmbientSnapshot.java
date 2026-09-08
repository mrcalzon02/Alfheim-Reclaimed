package com.continuityworks.alfheimcompanion.brain;

import java.util.List;
import java.util.UUID;

public record AmbientSnapshot(
        long requestId,
        long gameTime,
        UUID companionUuid,
        UUID ownerUuid,
        String dimension,
        String biome,
        String timeOfDay,
        String weather,
        String activity,
        String activeQuest,
        String personality,
        String combatProfile,
        List<String> relevantMemories
) {
    public AmbientSnapshot { relevantMemories = List.copyOf(relevantMemories); }
}

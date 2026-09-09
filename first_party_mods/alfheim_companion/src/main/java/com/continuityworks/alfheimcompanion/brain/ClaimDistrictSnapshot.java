package com.continuityworks.alfheimcompanion.brain;

import net.minecraft.world.level.ChunkPos;

import java.util.UUID;

/** Immutable value comparison for keeping or relocating a companion claim district. */
public record ClaimDistrictSnapshot(long requestId, UUID ownerUuid, String dimensionId,
                                    ChunkPos currentCenter, ChunkPos candidateCenter,
                                    int currentValue, int candidateValue, String behaviorPreset,
                                    String currentReasons, String candidateReasons) {
    public ClaimDistrictSnapshot {
        if (ownerUuid == null || currentCenter == null || candidateCenter == null)
            throw new IllegalArgumentException("claim district identity");
        dimensionId = limit(dimensionId, 96);
        behaviorPreset = limit(behaviorPreset, 24);
        currentReasons = limit(currentReasons, 160);
        candidateReasons = limit(candidateReasons, 160);
        currentValue = Math.max(0, Math.min(100, currentValue));
        candidateValue = Math.max(0, Math.min(100, candidateValue));
    }

    private static String limit(String value, int maximum) {
        if (value == null) return "";
        String clean = value.replace('\n', ' ').replace('\r', ' ').strip();
        return clean.length() <= maximum ? clean : clean.substring(0, maximum);
    }
}

package com.continuityworks.alfheimcompanion.brain;

import java.util.List;
import java.util.UUID;

/** Compact immutable evidence for a slow autonomous-work choice. No coordinates or block actions are exposed. */
public record AutonomousActivitySnapshot(long requestId, UUID ownerUuid, String behaviorPreset,
                                         int nutrition, int stamina, int claimCount,
                                         String previousChoice, List<AutonomousActivityOption> options) {
    public AutonomousActivitySnapshot {
        if (ownerUuid == null) throw new IllegalArgumentException("ownerUuid");
        behaviorPreset = limit(behaviorPreset, 24);
        nutrition = Math.max(0, Math.min(20, nutrition));
        stamina = Math.max(0, Math.min(100, stamina));
        claimCount = Math.max(0, Math.min(25, claimCount));
        previousChoice = limit(previousChoice, 40);
        options = List.copyOf(options == null ? List.of() : options);
        if (options.isEmpty() || options.size() > 6) throw new IllegalArgumentException("activity options");
    }

    public boolean offers(String id) {
        return options.stream().anyMatch(option -> option.id().equals(id));
    }

    private static String limit(String value, int maximum) {
        if (value == null) return "";
        String clean = value.strip();
        return clean.length() <= maximum ? clean : clean.substring(0, maximum);
    }
}

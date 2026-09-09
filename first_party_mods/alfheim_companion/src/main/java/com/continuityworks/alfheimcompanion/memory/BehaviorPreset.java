package com.continuityworks.alfheimcompanion.memory;

import java.util.Locale;
import java.util.Optional;

/** Stable preference weights. Safety and permission gates always outrank these preferences. */
public enum BehaviorPreset {
    BALANCED("balanced", 50, 50, 50, 25),
    WARDEN("warden", 85, 35, 25, 30),
    WAYFINDER("wayfinder", 45, 75, 25, 25),
    ARTISAN("artisan", 30, 45, 90, 30),
    STEWARD("steward", 55, 55, 75, 40);

    private final String id;
    private final int combatWeight;
    private final int questWeight;
    private final int buildWeight;
    private final int recoveryFloor;

    BehaviorPreset(String id, int combatWeight, int questWeight, int buildWeight, int recoveryFloor) {
        this.id = id;
        this.combatWeight = combatWeight;
        this.questWeight = questWeight;
        this.buildWeight = buildWeight;
        this.recoveryFloor = recoveryFloor;
    }

    public String id() { return id; }
    public int combatWeight() { return combatWeight; }
    public int questWeight() { return questWeight; }
    public int buildWeight() { return buildWeight; }
    public int recoveryFloor() { return recoveryFloor; }

    public static Optional<BehaviorPreset> parse(String value) {
        if (value == null) return Optional.empty();
        String normalized = value.strip().toLowerCase(Locale.ROOT).replace(' ', '_');
        for (BehaviorPreset preset : values()) {
            if (preset.id.equals(normalized) || preset.name().equalsIgnoreCase(normalized))
                return Optional.of(preset);
        }
        return Optional.empty();
    }
}

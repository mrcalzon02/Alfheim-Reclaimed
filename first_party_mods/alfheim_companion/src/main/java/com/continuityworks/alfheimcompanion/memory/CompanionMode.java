package com.continuityworks.alfheimcompanion.memory;

public enum CompanionMode {
    FOLLOWING,
    WAITING,
    GUARDING,
    DEFENDING,
    RETREATING,
    WORKING,
    DISMISSED;

    public static CompanionMode parse(String value) {
        try {
            return CompanionMode.valueOf(value);
        } catch (IllegalArgumentException | NullPointerException ignored) {
            return FOLLOWING;
        }
    }
}

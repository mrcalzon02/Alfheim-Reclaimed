package com.continuityworks.alfheimcompanion.brain;

/** One Java-authored activity the inference model is permitted to select. */
public record AutonomousActivityOption(String id, AutonomousActivityKind kind, int value,
                                       String reason, boolean changesWorld,
                                       boolean ownerApprovalRequired) {
    public AutonomousActivityOption {
        if (id == null || !id.matches("[A-Z0-9_]{2,40}"))
            throw new IllegalArgumentException("activity id");
        kind = kind == null ? AutonomousActivityKind.NONE : kind;
        value = Math.max(0, Math.min(100, value));
        reason = limit(reason, 96);
    }

    private static String limit(String value, int maximum) {
        if (value == null) return "";
        String clean = value.replace('\n', ' ').replace('\r', ' ').strip();
        return clean.length() <= maximum ? clean : clean.substring(0, maximum);
    }
}

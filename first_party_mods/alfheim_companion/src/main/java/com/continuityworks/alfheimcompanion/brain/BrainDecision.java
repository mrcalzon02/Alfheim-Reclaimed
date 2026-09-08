package com.continuityworks.alfheimcompanion.brain;

public record BrainDecision(
        long requestId,
        BrainDirective directive,
        int targetEntityId,
        String taskKey,
        String dialogue
) {
    public BrainDecision {
        taskKey = limit(taskKey, 64);
        dialogue = limit(dialogue, 120);
    }

    private static String limit(String value, int maximum) {
        if (value == null) return "";
        return value.length() <= maximum ? value : value.substring(0, maximum);
    }
}

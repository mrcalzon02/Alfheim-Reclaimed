package com.continuityworks.alfheimcompanion.brain;

public record BrainDecision(
        long requestId,
        BrainDirective directive,
        int targetEntityId,
        String taskKey,
        String selectedActionId,
        String selectedSkillId,
        String responseKey,
        String dialogue
) {
    public BrainDecision {
        taskKey = limit(taskKey, 64);
        selectedActionId = limit(selectedActionId, 40);
        selectedSkillId = limit(selectedSkillId, 64);
        responseKey = limit(responseKey, 48);
        dialogue = limit(dialogue, 120);
    }

    public BrainDecision(long requestId, BrainDirective directive, int targetEntityId, String taskKey,
                         String selectedSkillId, String responseKey, String dialogue) {
        this(requestId, directive, targetEntityId, taskKey, defaultAction(directive), selectedSkillId,
                responseKey, dialogue);
    }

    private static String defaultAction(BrainDirective directive) {
        return switch (directive) {
            case ADVISE, IDLE -> "ANSWER_ONLY";
            case DEFEND -> "DEFEND_NEAREST";
            case RETREAT -> "RETREAT_TO_OWNER";
            case FOLLOW -> "FOLLOW_OWNER";
            case WAIT -> "HOLD_POSITION";
            case EXECUTE_TASK, REQUEST_BLUEPRINT -> "CONTINUE_TASK";
        };
    }

    private static String limit(String value, int maximum) {
        if (value == null) return "";
        return value.length() <= maximum ? value : value.substring(0, maximum);
    }
}

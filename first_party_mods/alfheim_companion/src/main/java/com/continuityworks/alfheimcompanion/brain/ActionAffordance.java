package com.continuityworks.alfheimcompanion.brain;

/** A Java-registered action the model may select; arbitrary model-authored actions are impossible. */
public record ActionAffordance(String id, String label, BrainDirective directive, int targetEntityId,
                               String taskKey, ActivityBaseline baseline, boolean ownerApprovalRequired) {
    public ActionAffordance {
        if (id == null || !id.matches("[A-Z0-9_]{2,40}")) throw new IllegalArgumentException("action id");
        label = limit(label, 80);
        directive = directive == null ? BrainDirective.IDLE : directive;
        taskKey = limit(taskKey, 64);
        baseline = baseline == null ? ActivityBaseline.COMPANIONSHIP : baseline;
    }

    private static String limit(String value, int maximum) {
        if (value == null) return "";
        return value.length() <= maximum ? value : value.substring(0, maximum);
    }
}

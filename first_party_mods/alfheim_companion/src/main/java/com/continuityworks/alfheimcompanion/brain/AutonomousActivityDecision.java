package com.continuityworks.alfheimcompanion.brain;

/** The model can return only an offered activity ID; Java derives every target and action. */
public record AutonomousActivityDecision(long requestId, String selectedOptionId) {
    public AutonomousActivityDecision {
        if (selectedOptionId == null || !selectedOptionId.matches("[A-Z0-9_]{2,40}"))
            throw new IllegalArgumentException("selectedOptionId");
    }
}

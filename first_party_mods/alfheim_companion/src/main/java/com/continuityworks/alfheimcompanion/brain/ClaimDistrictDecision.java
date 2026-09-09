package com.continuityworks.alfheimcompanion.brain;

public record ClaimDistrictDecision(long requestId, Choice choice) {
    public enum Choice { KEEP_DISTRICT, RELOCATE_DISTRICT }

    public ClaimDistrictDecision {
        choice = choice == null ? Choice.KEEP_DISTRICT : choice;
    }
}

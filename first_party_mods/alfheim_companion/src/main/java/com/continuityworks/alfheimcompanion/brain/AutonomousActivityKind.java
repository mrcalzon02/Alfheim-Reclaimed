package com.continuityworks.alfheimcompanion.brain;

/** Stable activity families. World-changing families remain unavailable until their executors exist. */
public enum AutonomousActivityKind {
    NONE,
    RECOVER_AT_BASE,
    PATROL_CLAIMS,
    SURVEY_DISTRICT,
    INSPECT_BASE,
    TEND_FARM,
    MINE_RESOURCES,
    PROPOSE_CONSTRUCTION
}

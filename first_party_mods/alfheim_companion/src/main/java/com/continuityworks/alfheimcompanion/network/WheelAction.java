package com.continuityworks.alfheimcompanion.network;

public enum WheelAction {
    SUMMON_RECALL("Summon / Recall"),
    FOLLOW("Follow"),
    WAIT("Wait Here"),
    GUARD("Guard Here"),
    STATUS("Status"),
    CANCEL_TASK("Cancel Task"),
    DISMISS("Dismiss"),
    DEFEND("Defend Me");

    private final String label;

    WheelAction(String label) { this.label = label; }
    public String label() { return label; }
}

package com.continuityworks.alfheimcompanion.service;

/** Pure policy for a singleton companion leased to different players. */
public final class CompanionHandoffRules {
    private CompanionHandoffRules() {}

    public enum Decision {
        SAME_OWNER,
        SAVE_LOADED_COMPANION,
        TRANSFER_DISMISSED,
        BLOCK_UNLOADED_ACTIVE,
        BLOCK_OWNER_MISMATCH
    }

    public static Decision evaluate(boolean changingOwner, boolean loaded,
                                    boolean dismissed, boolean ownerMatches) {
        if (!changingOwner) return Decision.SAME_OWNER;
        if (loaded) return ownerMatches ? Decision.SAVE_LOADED_COMPANION
                                       : Decision.BLOCK_OWNER_MISMATCH;
        return dismissed ? Decision.TRANSFER_DISMISSED : Decision.BLOCK_UNLOADED_ACTIVE;
    }
}

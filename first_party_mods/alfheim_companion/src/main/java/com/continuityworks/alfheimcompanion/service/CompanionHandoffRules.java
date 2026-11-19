package com.continuityworks.alfheimcompanion.service;

/** Pure policy for a singleton companion's presence and player lease handoff. */
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
        // A missing but still-active entity is NOT an invitation to spawn a replacement.
        // This applies even when the same player owns the lease. Otherwise the original
        // (possibly carrying valuable items in an unloaded chunk) becomes orphaned.
        if (!loaded && !dismissed) return Decision.BLOCK_UNLOADED_ACTIVE;
        // Never trust only the persistent lease when the loaded entity says otherwise.
        if (loaded && !ownerMatches) return Decision.BLOCK_OWNER_MISMATCH;
        if (!changingOwner) return Decision.SAME_OWNER;
        return loaded ? Decision.SAVE_LOADED_COMPANION : Decision.TRANSFER_DISMISSED;
    }
}

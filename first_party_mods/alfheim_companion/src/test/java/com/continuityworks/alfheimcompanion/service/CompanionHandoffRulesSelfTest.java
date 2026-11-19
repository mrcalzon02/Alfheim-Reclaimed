package com.continuityworks.alfheimcompanion.service;

import com.continuityworks.alfheimcompanion.service.CompanionHandoffRules.Decision;

/** Standalone Java 17 policy regression; does not launch Minecraft. */
public final class CompanionHandoffRulesSelfTest {
    private CompanionHandoffRulesSelfTest() {}

    private static void assertDecision(Decision expected, boolean switching, boolean loaded,
                                       boolean dismissed, boolean matching) {
        Decision actual = CompanionHandoffRules.evaluate(switching, loaded, dismissed, matching);
        if (actual != expected) throw new AssertionError(
                "expected " + expected + " but got " + actual
                + ": switching=" + switching + ", loaded=" + loaded
                + ", dismissed=" + dismissed + ", matching=" + matching);
    }

    public static void main(String[] args) {
        // Both current-owner and cross-player attempts must protect missing active entities.
        assertDecision(Decision.SAME_OWNER, false, true, false, true);
        assertDecision(Decision.SAME_OWNER, false, true, true, true);
        assertDecision(Decision.BLOCK_UNLOADED_ACTIVE, false, false, false, false);
        assertDecision(Decision.BLOCK_UNLOADED_ACTIVE, false, false, false, true);
        assertDecision(Decision.SAME_OWNER, false, false, true, false);
        assertDecision(Decision.BLOCK_OWNER_MISMATCH, false, true, false, false);
        assertDecision(Decision.BLOCK_OWNER_MISMATCH, false, true, true, false);
        assertDecision(Decision.SAVE_LOADED_COMPANION, true, true, false, true);
        assertDecision(Decision.SAVE_LOADED_COMPANION, true, true, true, true);
        assertDecision(Decision.BLOCK_OWNER_MISMATCH, true, true, false, false);
        assertDecision(Decision.BLOCK_OWNER_MISMATCH, true, true, true, false);
        assertDecision(Decision.BLOCK_UNLOADED_ACTIVE, true, false, false, false);
        assertDecision(Decision.TRANSFER_DISMISSED, true, false, true, false);
        System.out.println("COMPANION_HANDOFF_RULES_PASS: both owners, unloaded-active refusal, entity-owner mismatch, safe dismissed replacement");
    }
}

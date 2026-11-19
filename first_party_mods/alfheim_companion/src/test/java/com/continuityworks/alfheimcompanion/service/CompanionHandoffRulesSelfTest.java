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
        assertDecision(Decision.SAME_OWNER, false, true, false, true);
        assertDecision(Decision.SAME_OWNER, false, false, false, false);
        assertDecision(Decision.SAVE_LOADED_COMPANION, true, true, false, true);
        assertDecision(Decision.SAVE_LOADED_COMPANION, true, true, true, true);
        assertDecision(Decision.BLOCK_OWNER_MISMATCH, true, true, false, false);
        assertDecision(Decision.BLOCK_OWNER_MISMATCH, true, true, true, false);
        assertDecision(Decision.BLOCK_UNLOADED_ACTIVE, true, false, false, false);
        assertDecision(Decision.TRANSFER_DISMISSED, true, false, true, false);
        System.out.println("COMPANION_HANDOFF_RULES_PASS: same owner, loaded-owner match/mismatch, unloaded active block, dismissed handoff");
    }
}

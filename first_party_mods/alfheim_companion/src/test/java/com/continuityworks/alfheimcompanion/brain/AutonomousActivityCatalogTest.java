package com.continuityworks.alfheimcompanion.brain;

import com.continuityworks.alfheimcompanion.memory.BehaviorPreset;
import org.junit.jupiter.api.Test;

import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;

class AutonomousActivityCatalogTest {
    @Test
    void lowNeedsOfferOnlyRecovery() {
        var options = AutonomousActivityCatalog.optionsFor(BehaviorPreset.WARDEN,
                6, 90, 12, AutonomousActivityKind.NONE);
        assertEquals(1, options.size());
        assertEquals(AutonomousActivityKind.RECOVER_AT_BASE, options.get(0).kind());
    }

    @Test
    void healthyMenuContainsOnlyImplementedReadOnlyActivities() {
        var options = AutonomousActivityCatalog.optionsFor(BehaviorPreset.ARTISAN,
                20, 100, 25, AutonomousActivityKind.NONE);
        assertEquals(4, options.size());
        assertTrue(options.stream().noneMatch(AutonomousActivityOption::changesWorld));
        assertTrue(options.stream().noneMatch(AutonomousActivityOption::ownerApprovalRequired));
        assertTrue(options.stream().noneMatch(option -> option.kind() == AutonomousActivityKind.MINE_RESOURCES
                || option.kind() == AutonomousActivityKind.TEND_FARM
                || option.kind() == AutonomousActivityKind.PROPOSE_CONSTRUCTION));
    }

    @Test
    void deterministicEngineReturnsOneOfferedIdentifier() {
        var options = AutonomousActivityCatalog.optionsFor(BehaviorPreset.WAYFINDER,
                20, 100, 9, AutonomousActivityKind.NONE);
        var snapshot = new AutonomousActivitySnapshot(14, UUID.randomUUID(), "wayfinder",
                20, 100, 9, "", options);
        AutonomousActivityDecision decision = new RuleBasedTinyBrainEngine()
                .chooseAutonomousActivity(snapshot).join();
        assertTrue(snapshot.offers(decision.selectedOptionId()));
        assertEquals(options.get(0).id(), decision.selectedOptionId());
    }

    @Test
    void repetitionPenaltyChangesTheLeadingChoice() {
        var first = AutonomousActivityCatalog.optionsFor(BehaviorPreset.ARTISAN,
                20, 100, 8, AutonomousActivityKind.NONE);
        var second = AutonomousActivityCatalog.optionsFor(BehaviorPreset.ARTISAN,
                20, 100, 8, first.get(0).kind());
        assertNotEquals(first.get(0).id(), second.get(0).id());
    }
}

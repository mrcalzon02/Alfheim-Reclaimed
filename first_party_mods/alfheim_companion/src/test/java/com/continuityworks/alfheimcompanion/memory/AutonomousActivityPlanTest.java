package com.continuityworks.alfheimcompanion.memory;

import com.continuityworks.alfheimcompanion.brain.AutonomousActivityKind;
import net.minecraft.core.BlockPos;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class AutonomousActivityPlanTest {
    @Test
    void completedPlanRoundTripsAsAuditHistory() {
        var original = new AutonomousActivityPlan(AutonomousActivityPlan.State.COMPLETE,
                "SURVEY_DISTRICT", AutonomousActivityKind.SURVEY_DISTRICT,
                "minecraft:overworld", new BlockPos(40, 72, -16), 100,
                1200, 1400, "relief=3,wet_samples=0/9");
        assertEquals(original, AutonomousActivityPlan.load(original.save()));
    }

    @Test
    void restartPausesRuntimeNavigation() {
        var traveling = new AutonomousActivityPlan(AutonomousActivityPlan.State.TRAVELING,
                "PATROL_CLAIMS", AutonomousActivityKind.PATROL_CLAIMS,
                "minecraft:overworld", new BlockPos(8, 70, 8), 25,
                100, 120, "traveling");
        var loaded = AutonomousActivityPlan.load(traveling.save());
        assertEquals(AutonomousActivityPlan.State.PAUSED, loaded.state());
        assertFalse(loaded.active());
        assertEquals(traveling.target(), loaded.target());
    }

    @Test
    void corruptStateFailsClosed() {
        var tag = AutonomousActivityPlan.NONE.save();
        tag.putString("kind", "DIG_EVERYTHING");
        assertEquals(AutonomousActivityPlan.NONE, AutonomousActivityPlan.load(tag));
    }
}

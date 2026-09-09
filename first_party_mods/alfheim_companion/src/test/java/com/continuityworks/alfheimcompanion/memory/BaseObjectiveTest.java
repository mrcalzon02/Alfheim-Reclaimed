package com.continuityworks.alfheimcompanion.memory;

import net.minecraft.core.BlockPos;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class BaseObjectiveTest {
    @Test
    void roundTripsPersistentPhaseAndAnchor() {
        BaseObjective original = new BaseObjective(BaseObjective.Phase.AWAITING_APPROVAL,
                "minecraft:overworld", new BlockPos(12, 70, -8), "quiet workshop", 40, 80);
        BaseObjective loaded = BaseObjective.load(original.save());
        assertEquals(original, loaded);
        assertTrue(loaded.active());
        assertFalse(loaded.established());
    }

    @Test
    void rejectsUnknownPhaseAndBoundsPurpose() {
        var tag = BaseObjective.NONE.save();
        tag.putString("phase", "invented");
        assertEquals(BaseObjective.NONE, BaseObjective.load(tag));
        assertEquals(96, new BaseObjective(BaseObjective.Phase.SURVEY, "minecraft:overworld",
                BlockPos.ZERO, "x".repeat(200), 0, 0).purpose().length());
    }
}

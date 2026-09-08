package com.continuityworks.alfheimcompanion.network;

import org.junit.jupiter.api.Test;

import java.util.Arrays;

import static org.junit.jupiter.api.Assertions.*;

class WheelActionTest {
    @Test
    void firstWheelIsBoundedAndEverySegmentHasAUniqueLabel() {
        assertEquals(8, WheelAction.values().length);
        assertEquals(8, Arrays.stream(WheelAction.values()).map(WheelAction::label).distinct().count());
        assertTrue(Arrays.stream(WheelAction.values()).noneMatch(action -> action.label().isBlank()));
    }
}

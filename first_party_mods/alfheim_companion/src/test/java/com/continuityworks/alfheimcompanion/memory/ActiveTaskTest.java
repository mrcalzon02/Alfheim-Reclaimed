package com.continuityworks.alfheimcompanion.memory;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class ActiveTaskTest {
    @Test
    void structuredTaskRoundTripsAndBoundsInput() {
        ActiveTask original = new ActiveTask(ActiveTask.Kind.ITEM, "fetch|unsafe",
                "x".repeat(100), 900, 42);
        ActiveTask loaded = ActiveTask.load(original.save());
        assertEquals(ActiveTask.Kind.ITEM, loaded.kind());
        assertFalse(loaded.action().contains("|"));
        assertEquals(64, loaded.target().length());
        assertEquals(64, loaded.count());
        assertEquals(42, loaded.createdGameTime());
    }

    @Test
    void migratesVersionOneTasksAndRejectsMalformedCounts() {
        ActiveTask craft = ActiveTask.migrate("craft|4|oak planks");
        assertEquals(ActiveTask.Kind.CRAFT, craft.kind());
        assertEquals(4, craft.count());
        assertEquals("oak planks", craft.target());
        assertTrue(ActiveTask.migrate("craft|not-a-number|stone").isNone());
        assertTrue(ActiveTask.migrate("unknown|payload").isNone());
    }
}

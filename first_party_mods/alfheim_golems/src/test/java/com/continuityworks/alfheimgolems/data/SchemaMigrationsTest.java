package com.continuityworks.alfheimgolems.data;

import net.minecraft.nbt.CompoundTag;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class SchemaMigrationsTest {
    @Test
    void runsEveryStepAndStampsFinalVersion() {
        SchemaMigrations migrations = new SchemaMigrations(2)
                .register(0, tag -> { tag.putBoolean("zero", true); return tag; })
                .register(1, tag -> { tag.putBoolean("one", true); return tag; });
        CompoundTag result = migrations.migrate(new CompoundTag(), 0);
        assertTrue(result.getBoolean("zero"));
        assertTrue(result.getBoolean("one"));
        assertEquals(2, result.getInt("DataVersion"));
    }

    @Test
    void missingDuplicateAndFutureStepsFailClosed() {
        SchemaMigrations missing = new SchemaMigrations(2).register(0, tag -> tag);
        assertThrows(IllegalStateException.class, () -> missing.migrate(new CompoundTag(), 0));
        assertThrows(IllegalArgumentException.class, () -> missing.migrate(new CompoundTag(), 3));

        SchemaMigrations duplicate = new SchemaMigrations(1).register(0, tag -> tag);
        assertThrows(IllegalArgumentException.class, () -> duplicate.register(0, tag -> tag));
    }
}

package com.continuityworks.alfheimgolems.data;

import net.minecraft.nbt.CompoundTag;

import java.util.Map;
import java.util.TreeMap;
import java.util.function.UnaryOperator;

/** Sequential, explicit SavedData migrations. Missing steps fail instead of guessing. */
public final class SchemaMigrations {
    private final int currentVersion;
    private final Map<Integer, UnaryOperator<CompoundTag>> steps = new TreeMap<>();

    public SchemaMigrations(int currentVersion) {
        if (currentVersion < 1) throw new IllegalArgumentException("currentVersion must be positive");
        this.currentVersion = currentVersion;
    }

    public SchemaMigrations register(int fromVersion, UnaryOperator<CompoundTag> migration) {
        if (fromVersion < 0 || fromVersion >= currentVersion) {
            throw new IllegalArgumentException("migration source is outside supported history");
        }
        if (steps.putIfAbsent(fromVersion, migration) != null) {
            throw new IllegalArgumentException("duplicate migration from version " + fromVersion);
        }
        return this;
    }

    public CompoundTag migrate(CompoundTag source, int fromVersion) {
        if (fromVersion < 0 || fromVersion > currentVersion) {
            throw new IllegalArgumentException("unsupported data version " + fromVersion);
        }
        CompoundTag result = source.copy();
        for (int version = fromVersion; version < currentVersion; version++) {
            UnaryOperator<CompoundTag> step = steps.get(version);
            if (step == null) throw new IllegalStateException("missing migration from version " + version);
            result = step.apply(result);
            result.putInt("DataVersion", version + 1);
        }
        return result;
    }
}

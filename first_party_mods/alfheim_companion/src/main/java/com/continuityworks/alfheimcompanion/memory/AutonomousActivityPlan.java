package com.continuityworks.alfheimcompanion.memory;

import com.continuityworks.alfheimcompanion.brain.AutonomousActivityKind;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;

/** Persisted audit state for one bounded autonomous activity. */
public record AutonomousActivityPlan(State state, String optionId, AutonomousActivityKind kind,
                                     String dimensionId, BlockPos target, int progress,
                                     long createdGameTime, long updatedGameTime, String note) {
    public enum State { NONE, SELECTED, TRAVELING, OBSERVING, COMPLETE, PAUSED }

    public static final AutonomousActivityPlan NONE = new AutonomousActivityPlan(State.NONE, "",
            AutonomousActivityKind.NONE, "minecraft:overworld", BlockPos.ZERO, 0, 0, 0, "");

    public AutonomousActivityPlan {
        state = state == null ? State.NONE : state;
        optionId = limit(optionId, 40);
        kind = kind == null ? AutonomousActivityKind.NONE : kind;
        dimensionId = limit(dimensionId, 96);
        target = target == null ? BlockPos.ZERO : target.immutable();
        progress = Math.max(0, Math.min(100, progress));
        createdGameTime = Math.max(0, createdGameTime);
        updatedGameTime = Math.max(createdGameTime, updatedGameTime);
        note = limit(note, 96);
        if (state == State.NONE) {
            optionId = "";
            kind = AutonomousActivityKind.NONE;
            progress = 0;
        }
    }

    public boolean active() {
        return state == State.SELECTED || state == State.TRAVELING || state == State.OBSERVING;
    }

    public AutonomousActivityPlan advance(State next, int nextProgress, long gameTime, String nextNote) {
        return new AutonomousActivityPlan(next, optionId, kind, dimensionId, target, nextProgress,
                createdGameTime, gameTime, nextNote);
    }

    public CompoundTag save() {
        CompoundTag tag = new CompoundTag();
        tag.putString("state", state.name());
        tag.putString("option", optionId);
        tag.putString("kind", kind.name());
        tag.putString("dimension", dimensionId);
        tag.putLong("target", target.asLong());
        tag.putInt("progress", progress);
        tag.putLong("created", createdGameTime);
        tag.putLong("updated", updatedGameTime);
        tag.putString("note", note);
        return tag;
    }

    public static AutonomousActivityPlan load(CompoundTag tag) {
        if (tag == null || !tag.contains("state", Tag.TAG_STRING)) return NONE;
        try {
            State state = State.valueOf(tag.getString("state"));
            AutonomousActivityKind kind = AutonomousActivityKind.valueOf(tag.getString("kind"));
            // Navigation is runtime state. A restart keeps the audit record but never resumes blindly.
            if (state == State.SELECTED || state == State.TRAVELING || state == State.OBSERVING)
                state = State.PAUSED;
            return new AutonomousActivityPlan(state, tag.getString("option"), kind,
                    tag.getString("dimension"), BlockPos.of(tag.getLong("target")),
                    tag.getInt("progress"), tag.getLong("created"), tag.getLong("updated"),
                    tag.getString("note"));
        } catch (RuntimeException ignored) {
            return NONE;
        }
    }

    private static String limit(String value, int maximum) {
        if (value == null) return "";
        String clean = value.replace('\n', ' ').replace('\r', ' ').strip();
        return clean.length() <= maximum ? clean : clean.substring(0, maximum);
    }
}

package com.continuityworks.alfheimcompanion.memory;

import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;

import java.util.Locale;

/** Persistent, bounded progress for an explicitly requested companion base. */
public record BaseObjective(Phase phase, String dimensionId, BlockPos anchor, String purpose,
                            long createdGameTime, long updatedGameTime) {
    public enum Phase {
        NONE, SURVEY, PROPOSING, AWAITING_APPROVAL, BUILDING, FURNISHING, MAINTAINING, PAUSED
    }

    public static final BaseObjective NONE = new BaseObjective(Phase.NONE, "", BlockPos.ZERO,
            "", 0, 0);

    public BaseObjective {
        phase = phase == null ? Phase.NONE : phase;
        dimensionId = limit(dimensionId, 96);
        anchor = anchor == null ? BlockPos.ZERO : anchor.immutable();
        purpose = limit(purpose, 96);
        createdGameTime = Math.max(0, createdGameTime);
        updatedGameTime = Math.max(createdGameTime, updatedGameTime);
    }

    public boolean active() {
        return phase != Phase.NONE && phase != Phase.MAINTAINING;
    }

    public boolean established() {
        return phase == Phase.FURNISHING || phase == Phase.MAINTAINING;
    }

    public BaseObjective advance(Phase next, long gameTime) {
        return new BaseObjective(next, dimensionId, anchor, purpose, createdGameTime, gameTime);
    }

    public CompoundTag save() {
        CompoundTag tag = new CompoundTag();
        tag.putString("phase", phase.name());
        tag.putString("dimension", dimensionId);
        tag.putLong("anchor", anchor.asLong());
        tag.putString("purpose", purpose);
        tag.putLong("created", createdGameTime);
        tag.putLong("updated", updatedGameTime);
        return tag;
    }

    public static BaseObjective load(CompoundTag tag) {
        if (tag == null || !tag.contains("phase", Tag.TAG_STRING)) return NONE;
        Phase phase;
        try { phase = Phase.valueOf(tag.getString("phase").toUpperCase(Locale.ROOT)); }
        catch (IllegalArgumentException ignored) { return NONE; }
        return new BaseObjective(phase, tag.getString("dimension"),
                tag.contains("anchor", Tag.TAG_LONG) ? BlockPos.of(tag.getLong("anchor")) : BlockPos.ZERO,
                tag.getString("purpose"), tag.getLong("created"), tag.getLong("updated"));
    }

    private static String limit(String value, int maximum) {
        if (value == null) return "";
        String clean = value.replace('|', ' ').strip();
        return clean.length() <= maximum ? clean : clean.substring(0, maximum);
    }
}

package com.continuityworks.alfheimcompanion.memory;

import net.minecraft.nbt.CompoundTag;

import java.util.Locale;
import java.util.UUID;

/** Small restart-safe blueprint audit record; block lists remain in the provider/runtime cache. */
public record BlueprintLedger(UUID requestId, UUID blueprintId, State state, String purpose,
                              String integrityHash, int placementCount, int completedPlacements,
                              String message, long updatedGameTime) {
    public enum State { NONE, REQUESTED, PREVIEW, APPROVED, EXECUTING, COMPLETE, REJECTED, FAILED, PAUSED }

    public static final BlueprintLedger NONE = new BlueprintLedger(null, null, State.NONE,
            "", "", 0, 0, "", 0);

    public BlueprintLedger {
        state = state == null ? State.NONE : state;
        purpose = limit(purpose, 64);
        integrityHash = limit(integrityHash, 128);
        placementCount = Math.max(0, Math.min(8192, placementCount));
        completedPlacements = Math.max(0, Math.min(placementCount, completedPlacements));
        message = limit(message, 160);
        updatedGameTime = Math.max(0, updatedGameTime);
    }

    public boolean active() {
        return state == State.REQUESTED || state == State.PREVIEW || state == State.APPROVED
                || state == State.EXECUTING || state == State.PAUSED;
    }

    public CompoundTag save() {
        CompoundTag tag = new CompoundTag();
        if (requestId != null) tag.putUUID("request", requestId);
        if (blueprintId != null) tag.putUUID("blueprint", blueprintId);
        tag.putString("state", state.name());
        tag.putString("purpose", purpose);
        tag.putString("hash", integrityHash);
        tag.putInt("placements", placementCount);
        tag.putInt("completed", completedPlacements);
        tag.putString("message", message);
        tag.putLong("updated", updatedGameTime);
        return tag;
    }

    public static BlueprintLedger load(CompoundTag tag) {
        State state;
        try { state = State.valueOf(tag.getString("state").toUpperCase(Locale.ROOT)); }
        catch (IllegalArgumentException ignored) { return NONE; }
        // A proposal list is deliberately not persisted. Interrupted work must be regenerated.
        if (state == State.PREVIEW || state == State.APPROVED || state == State.EXECUTING) state = State.PAUSED;
        return new BlueprintLedger(tag.hasUUID("request") ? tag.getUUID("request") : null,
                tag.hasUUID("blueprint") ? tag.getUUID("blueprint") : null, state,
                tag.getString("purpose"), tag.getString("hash"), tag.getInt("placements"),
                tag.getInt("completed"), tag.getString("message"), tag.getLong("updated"));
    }

    private static String limit(String value, int maximum) {
        if (value == null) return "";
        return value.length() <= maximum ? value : value.substring(0, maximum);
    }
}

package com.continuityworks.alfheimcompanion.memory;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;

import java.util.Locale;

/** Versioned, bounded task state. Unknown/corrupt values safely become NONE. */
public record ActiveTask(Kind kind, String action, String target, int count, long createdGameTime) {
    public enum Kind { NONE, FOLLOW, GUARD, ITEM, CRAFT, BUILD, BASE }

    public static final ActiveTask NONE = new ActiveTask(Kind.NONE, "", "", 0, 0);

    public ActiveTask {
        kind = kind == null ? Kind.NONE : kind;
        action = limit(action, 16);
        target = limit(target, 64);
        count = kind == Kind.NONE ? 0 : Math.max(1, Math.min(64, count));
        createdGameTime = Math.max(0, createdGameTime);
    }

    public boolean isNone() { return kind == Kind.NONE; }

    public String display() {
        return switch (kind) {
            case NONE -> "";
            case FOLLOW -> "follow";
            case GUARD -> "guard here";
            case ITEM -> action + " " + count + " " + target;
            case CRAFT -> "help craft " + count + " " + target;
            case BUILD -> "help build " + target;
            case BASE -> "establish base: " + action.toLowerCase(Locale.ROOT).replace('_', ' ');
        };
    }

    public CompoundTag save() {
        CompoundTag tag = new CompoundTag();
        tag.putString("kind", kind.name());
        tag.putString("action", action);
        tag.putString("target", target);
        tag.putInt("count", count);
        tag.putLong("created", createdGameTime);
        return tag;
    }

    public static ActiveTask load(CompoundTag tag) {
        if (tag == null || !tag.contains("kind", Tag.TAG_STRING)) return NONE;
        Kind kind;
        try { kind = Kind.valueOf(tag.getString("kind").toUpperCase(Locale.ROOT)); }
        catch (IllegalArgumentException ignored) { return NONE; }
        return new ActiveTask(kind, tag.getString("action"), tag.getString("target"),
                tag.getInt("count"), tag.getLong("created"));
    }

    /** Reads version-1 pipe-delimited saves without ever executing their contents. */
    public static ActiveTask migrate(String legacy) {
        if (legacy == null || legacy.isBlank()) return NONE;
        String[] parts = legacy.split("\\|", 4);
        try {
            return switch (parts[0]) {
                case "guard" -> new ActiveTask(Kind.GUARD, "", "", 1, 0);
                case "build" -> new ActiveTask(Kind.BUILD, "", parts.length > 1 ? parts[1] : "", 1, 0);
                case "base" -> new ActiveTask(Kind.BASE, parts.length > 1 ? parts[1] : "SURVEY",
                        parts.length > 2 ? parts[2] : "base of operations", 1, 0);
                case "craft" -> new ActiveTask(Kind.CRAFT, "", parts.length > 2 ? parts[2] : "",
                        parts.length > 1 ? Integer.parseInt(parts[1]) : 1, 0);
                case "item" -> new ActiveTask(Kind.ITEM, parts.length > 1 ? parts[1] : "show",
                        parts.length > 3 ? parts[3] : "", parts.length > 2 ? Integer.parseInt(parts[2]) : 1, 0);
                default -> NONE;
            };
        } catch (RuntimeException ignored) {
            return NONE;
        }
    }

    private static String limit(String value, int maximum) {
        if (value == null) return "";
        String clean = value.replace('|', ' ').strip();
        return clean.length() <= maximum ? clean : clean.substring(0, maximum);
    }
}

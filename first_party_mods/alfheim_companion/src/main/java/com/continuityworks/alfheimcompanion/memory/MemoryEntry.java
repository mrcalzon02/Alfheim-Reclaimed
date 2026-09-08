package com.continuityworks.alfheimcompanion.memory;

import net.minecraft.nbt.CompoundTag;

public record MemoryEntry(long gameTime, String type, String subject, String detail, int importance) {
    public MemoryEntry {
        type = limit(type, 32);
        subject = limit(subject, 64);
        detail = limit(detail, 240);
        importance = Math.max(0, Math.min(importance, 10));
    }

    public CompoundTag save() {
        CompoundTag tag = new CompoundTag();
        tag.putLong("time", gameTime);
        tag.putString("type", type);
        tag.putString("subject", subject);
        tag.putString("detail", detail);
        tag.putInt("importance", importance);
        return tag;
    }

    public static MemoryEntry load(CompoundTag tag) {
        return new MemoryEntry(tag.getLong("time"), tag.getString("type"),
                tag.getString("subject"), tag.getString("detail"), tag.getInt("importance"));
    }

    private static String limit(String value, int maximum) {
        if (value == null) return "";
        return value.length() <= maximum ? value : value.substring(0, maximum);
    }
}

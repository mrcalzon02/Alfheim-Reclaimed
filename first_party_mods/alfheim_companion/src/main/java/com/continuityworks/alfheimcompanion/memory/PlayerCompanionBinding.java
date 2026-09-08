package com.continuityworks.alfheimcompanion.memory;

import net.minecraft.nbt.CompoundTag;

public record PlayerCompanionBinding(String name, String outfit, boolean alive, int deaths) {
    public PlayerCompanionBinding {
        name = limit(name, 48);
        outfit = limit(outfit, 24);
        deaths = Math.max(0, deaths);
    }

    public CompoundTag save() {
        CompoundTag tag = new CompoundTag();
        tag.putString("name", name);
        tag.putString("outfit", outfit);
        tag.putBoolean("alive", alive);
        tag.putInt("deaths", deaths);
        return tag;
    }

    public static PlayerCompanionBinding load(CompoundTag tag) {
        return new PlayerCompanionBinding(tag.getString("name"), tag.getString("outfit"),
                !tag.contains("alive") || tag.getBoolean("alive"), tag.getInt("deaths"));
    }

    private static String limit(String value, int maximum) {
        if (value == null) return "";
        return value.length() <= maximum ? value : value.substring(0, maximum);
    }
}

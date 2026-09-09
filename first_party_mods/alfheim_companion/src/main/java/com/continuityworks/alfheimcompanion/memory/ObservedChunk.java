package com.continuityworks.alfheimcompanion.memory;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;

/** A full chunk encountered during ordinary travel; observing never causes chunk generation. */
public record ObservedChunk(String dimensionId, int chunkX, int chunkZ, long observedGameTime) {
    public ObservedChunk {
        dimensionId = dimensionId == null ? "" : dimensionId.replace('|', '/').strip();
        if (dimensionId.length() > 96) dimensionId = dimensionId.substring(0, 96);
        observedGameTime = Math.max(0, observedGameTime);
    }

    public String key() { return key(dimensionId, chunkX, chunkZ); }

    public CompoundTag save() {
        CompoundTag tag = new CompoundTag();
        tag.putString("dimension", dimensionId);
        tag.putInt("x", chunkX);
        tag.putInt("z", chunkZ);
        tag.putLong("observed", observedGameTime);
        return tag;
    }

    public static ObservedChunk load(CompoundTag tag) {
        if (tag == null || !tag.contains("dimension", Tag.TAG_STRING)) return null;
        return new ObservedChunk(tag.getString("dimension"), tag.getInt("x"), tag.getInt("z"),
                tag.getLong("observed"));
    }

    public static String key(String dimensionId, int x, int z) {
        return (dimensionId == null ? "" : dimensionId) + "|" + x + "|" + z;
    }
}

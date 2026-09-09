package com.continuityworks.alfheimcompanion.memory;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;

import java.util.UUID;

/** Audit record for a chunk claimed by consuming a companion Claim Paper. */
public record DelegatedClaim(UUID ownerUuid, String dimensionId, int chunkX, int chunkZ,
                             String purpose, long claimedGameTime) {
    public DelegatedClaim {
        if (ownerUuid == null) throw new IllegalArgumentException("ownerUuid");
        dimensionId = limit(dimensionId, 96);
        purpose = limit(purpose, 96);
        claimedGameTime = Math.max(0, claimedGameTime);
    }

    public String key() { return key(dimensionId, chunkX, chunkZ); }

    public CompoundTag save() {
        CompoundTag tag = new CompoundTag();
        tag.putUUID("owner", ownerUuid);
        tag.putString("dimension", dimensionId);
        tag.putInt("x", chunkX);
        tag.putInt("z", chunkZ);
        tag.putString("purpose", purpose);
        tag.putLong("claimed", claimedGameTime);
        return tag;
    }

    public static DelegatedClaim load(CompoundTag tag) {
        if (tag == null || !tag.hasUUID("owner") || !tag.contains("dimension", Tag.TAG_STRING)) return null;
        return new DelegatedClaim(tag.getUUID("owner"), tag.getString("dimension"), tag.getInt("x"),
                tag.getInt("z"), tag.getString("purpose"), tag.getLong("claimed"));
    }

    public static String key(String dimensionId, int x, int z) {
        return (dimensionId == null ? "" : dimensionId) + "|" + x + "|" + z;
    }

    private static String limit(String value, int maximum) {
        if (value == null) return "";
        String clean = value.replace('|', '/').strip();
        return clean.length() <= maximum ? clean : clean.substring(0, maximum);
    }
}

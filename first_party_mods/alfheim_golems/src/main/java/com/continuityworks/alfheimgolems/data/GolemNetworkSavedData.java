package com.continuityworks.alfheimgolems.data;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;

/**
 * Versioned server-global envelope. G0 stores counts only; later schemas add networks and orders
 * through explicit migrations. Future-version data opens read-only rather than being overwritten.
 */
public final class GolemNetworkSavedData extends SavedData {
    public static final String DATA_NAME = "alfheim_golems_networks";
    public static final int CURRENT_DATA_VERSION = 1;
    private static final SchemaMigrations MIGRATIONS = new SchemaMigrations(CURRENT_DATA_VERSION)
            .register(0, tag -> tag);

    private int loadedDataVersion = CURRENT_DATA_VERSION;
    private boolean readOnly;

    public static GolemNetworkSavedData get(MinecraftServer server) {
        GolemNetworkSavedData data = server.overworld().getDataStorage().computeIfAbsent(
                GolemNetworkSavedData::load, GolemNetworkSavedData::new, DATA_NAME);
        // A newly created empty envelope must still reach disk so schema/version reloads can be
        // validated and future migrations have a durable starting point. Never dirty data written
        // by a newer version: read-only mode exists specifically to prevent that overwrite.
        if (!data.readOnly) data.setDirty();
        return data;
    }

    public static GolemNetworkSavedData load(CompoundTag source) {
        int version = source.contains("DataVersion", Tag.TAG_INT) ? source.getInt("DataVersion") : 0;
        GolemNetworkSavedData data = new GolemNetworkSavedData();
        data.loadedDataVersion = version;
        if (version > CURRENT_DATA_VERSION) {
            data.readOnly = true;
            return data;
        }
        CompoundTag migrated = MIGRATIONS.migrate(source, version);
        data.loadedDataVersion = migrated.getInt("DataVersion");
        return data;
    }

    public int loadedDataVersion() {
        return loadedDataVersion;
    }

    public boolean readOnly() {
        return readOnly;
    }

    @Override
    public CompoundTag save(CompoundTag tag) {
        if (!readOnly) tag.putInt("DataVersion", CURRENT_DATA_VERSION);
        else tag.putInt("DataVersion", loadedDataVersion);
        tag.putInt("NetworkCount", 0);
        tag.putInt("OrderCount", 0);
        return tag;
    }
}

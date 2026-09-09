package com.continuityworks.alfheimgolems.data;

import net.minecraft.nbt.CompoundTag;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class GolemNetworkSavedDataTest {
    @Test
    void legacyEmptyEnvelopeMigratesToCurrentVersion() {
        GolemNetworkSavedData data = GolemNetworkSavedData.load(new CompoundTag());
        assertEquals(GolemNetworkSavedData.CURRENT_DATA_VERSION, data.loadedDataVersion());
        assertFalse(data.readOnly());
        assertEquals(GolemNetworkSavedData.CURRENT_DATA_VERSION,
                data.save(new CompoundTag()).getInt("DataVersion"));
    }

    @Test
    void futureEnvelopeRemainsReadOnlyAndKeepsItsVersion() {
        CompoundTag source = new CompoundTag();
        source.putInt("DataVersion", GolemNetworkSavedData.CURRENT_DATA_VERSION + 3);
        GolemNetworkSavedData data = GolemNetworkSavedData.load(source);
        assertTrue(data.readOnly());
        assertEquals(GolemNetworkSavedData.CURRENT_DATA_VERSION + 3,
                data.save(new CompoundTag()).getInt("DataVersion"));
    }
}

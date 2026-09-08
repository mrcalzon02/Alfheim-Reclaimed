package com.continuityworks.alfheimcompanion.memory;

import org.junit.jupiter.api.Test;

import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;

class PlayerBindingTest {
    @Test
    void bindingIsStableSelectableAndDeathGated() {
        CompanionSavedData data = new CompanionSavedData();
        UUID player = UUID.randomUUID();
        PlayerCompanionBinding first = data.getOrCreatePlayerBinding(player, 42);
        assertEquals(first, data.getOrCreatePlayerBinding(player, 999));
        assertTrue(data.setPlayerProfile(player, "Aelara", 1));
        assertTrue(data.setPlayerOutfit(player, "warden", 1));
        data.claimOrRefreshLease(player, 10);
        data.activatePlayerBinding(player, 10);
        data.markCurrentBindingDead();
        assertFalse(data.playerBinding(player).orElseThrow().alive());
        PlayerCompanionBinding reset = data.resetPlayerBinding(player, 500);
        assertTrue(reset.alive());
        assertEquals(1, reset.deaths());
    }
}

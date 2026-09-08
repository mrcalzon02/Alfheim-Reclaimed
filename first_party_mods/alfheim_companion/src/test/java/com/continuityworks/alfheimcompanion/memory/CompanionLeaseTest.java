package com.continuityworks.alfheimcompanion.memory;

import org.junit.jupiter.api.Test;

import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;

class CompanionLeaseTest {
    @Test
    void leaseIsExclusiveForThirtyMinutesAndThenExpires() {
        CompanionSavedData data = new CompanionSavedData();
        UUID first = UUID.randomUUID();
        UUID second = UUID.randomUUID();
        data.claimOrRefreshLease(first, 1000);
        assertEquals(37_000, data.leaseExpiresGameTime());
        assertTrue(data.leaseHeldByOther(second, 36_999));
        assertTrue(data.leaseHeldBy(first, 36_999));
        assertFalse(data.leaseHeldByOther(second, 37_000));
        assertFalse(data.leaseHeldBy(first, 37_000));
        assertTrue(data.expireLease(37_000));
        assertFalse(data.expireLease(37_001));
    }

    @Test
    void refreshingAndVoluntaryReleaseBehaveDeterministically() {
        CompanionSavedData data = new CompanionSavedData();
        UUID owner = UUID.randomUUID();
        data.claimOrRefreshLease(owner, 10);
        data.claimOrRefreshLease(owner, 100);
        assertEquals(36_100, data.leaseExpiresGameTime());
        data.releaseLease();
        assertEquals(0, data.leaseExpiresGameTime());
    }
}

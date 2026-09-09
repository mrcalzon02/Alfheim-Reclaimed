package com.continuityworks.alfheimcompanion.memory;

import org.junit.jupiter.api.Test;

import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;

class ClaimLedgerTest {
    @Test
    void observedAndDelegatedRecordsRoundTrip() {
        ObservedChunk observed = new ObservedChunk("mythicbotany:alfheim", 12, -7, 90);
        assertEquals(observed, ObservedChunk.load(observed.save()));

        DelegatedClaim claim = new DelegatedClaim(UUID.randomUUID(), "mythicbotany:alfheim",
                12, -7, "base of operations", 100);
        assertEquals(claim, DelegatedClaim.load(claim.save()));
        assertEquals("mythicbotany:alfheim|12|-7", claim.key());
    }
}

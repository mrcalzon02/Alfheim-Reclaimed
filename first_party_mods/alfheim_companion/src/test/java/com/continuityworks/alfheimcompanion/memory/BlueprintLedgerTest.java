package com.continuityworks.alfheimcompanion.memory;

import org.junit.jupiter.api.Test;

import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;

class BlueprintLedgerTest {
    @Test
    void interruptedExecutionLoadsPausedWithoutLosingAuditIdentity() {
        UUID request = UUID.randomUUID();
        UUID blueprint = UUID.randomUUID();
        BlueprintLedger executing = new BlueprintLedger(request, blueprint,
                BlueprintLedger.State.EXECUTING, "bridge", "sha256:abc", 400, 117, "building", 9000);
        BlueprintLedger restored = BlueprintLedger.load(executing.save());
        assertEquals(BlueprintLedger.State.PAUSED, restored.state());
        assertEquals(request, restored.requestId());
        assertEquals(blueprint, restored.blueprintId());
        assertEquals(117, restored.completedPlacements());
    }

    @Test
    void clampsUntrustedProgressAndText() {
        BlueprintLedger ledger = new BlueprintLedger(null, null, BlueprintLedger.State.PREVIEW,
                "x".repeat(100), "h".repeat(200), 100_000, 100_000, "m".repeat(300), -1);
        assertEquals(8192, ledger.placementCount());
        assertEquals(8192, ledger.completedPlacements());
        assertEquals(64, ledger.purpose().length());
        assertEquals(0, ledger.updatedGameTime());
    }
}

package com.continuityworks.alfheimgolems.inventory;

import com.continuityworks.alfheimgolems.order.FailureReason;
import com.continuityworks.alfheimgolems.order.ItemFilter;
import org.junit.jupiter.api.Test;

import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;

class TransferContractsTest {
    @Test
    void requestBoundsAndDistinctEndpointsAreEnforced() {
        UUID source = UUID.randomUUID();
        UUID destination = UUID.randomUUID();
        assertEquals(64, new TransferRequest(source, destination, ItemFilter.any(), 64).requestedCount());
        assertThrows(IllegalArgumentException.class,
                () -> new TransferRequest(source, source, ItemFilter.any(), 1));
        assertThrows(IllegalArgumentException.class,
                () -> new TransferRequest(source, destination, ItemFilter.any(), 0));
        assertThrows(IllegalArgumentException.class,
                () -> new TransferRequest(source, destination, ItemFilter.any(), 4097));
    }

    @Test
    void simulationNeverCommitsPastEitherCapacity() {
        assertEquals(12, new TransferSimulation(32, 12, FailureReason.NONE).transferable());
        assertEquals(0, new TransferSimulation(32, 12, FailureReason.PERMISSION_DENIED).transferable());
        assertThrows(IllegalArgumentException.class,
                () -> new TransferSimulation(-1, 2, FailureReason.NONE));
    }
}

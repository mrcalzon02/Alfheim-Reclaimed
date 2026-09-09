package com.continuityworks.alfheimgolems.inventory;

import com.continuityworks.alfheimgolems.order.ItemFilter;

import java.util.Objects;
import java.util.UUID;

public record TransferRequest(UUID sourceEndpointId, UUID destinationEndpointId,
                              ItemFilter filter, int requestedCount) {
    public static final int MAX_REQUESTED_COUNT = 4096;

    public TransferRequest {
        Objects.requireNonNull(sourceEndpointId, "sourceEndpointId");
        Objects.requireNonNull(destinationEndpointId, "destinationEndpointId");
        Objects.requireNonNull(filter, "filter");
        if (sourceEndpointId.equals(destinationEndpointId)) {
            throw new IllegalArgumentException("source and destination must differ");
        }
        if (requestedCount < 1 || requestedCount > MAX_REQUESTED_COUNT) {
            throw new IllegalArgumentException("requestedCount must be 1.." + MAX_REQUESTED_COUNT);
        }
    }
}

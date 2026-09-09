package com.continuityworks.alfheimgolems.inventory;

import com.continuityworks.alfheimgolems.order.FailureReason;

/** Immutable result of a no-mutation capacity and permission simulation. */
public record TransferSimulation(int extractable, int insertable, FailureReason failureReason) {
    public TransferSimulation {
        if (extractable < 0 || insertable < 0) {
            throw new IllegalArgumentException("simulated counts cannot be negative");
        }
        if (failureReason == null) failureReason = FailureReason.INTERNAL_ERROR;
    }

    public int transferable() {
        return failureReason == FailureReason.NONE ? Math.min(extractable, insertable) : 0;
    }

    public boolean canCommit() {
        return transferable() > 0;
    }
}

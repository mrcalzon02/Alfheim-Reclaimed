package com.continuityworks.alfheimgolems.diagnostic;

import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;

/** Bounded counters only: no player identity, coordinates or inventory contents. */
public final class GolemDiagnostics {
    private static final AtomicInteger ACTIVE_ORDERS = new AtomicInteger();
    private static final AtomicInteger PAUSED_ORDERS = new AtomicInteger();
    private static final AtomicInteger SLEEPING_GOLEMS = new AtomicInteger();
    private static final AtomicLong DECISIONS = new AtomicLong();
    private static final AtomicLong INVENTORY_MUTATIONS = new AtomicLong();

    private GolemDiagnostics() {}

    public static Snapshot snapshot() {
        return new Snapshot(ACTIVE_ORDERS.get(), PAUSED_ORDERS.get(), SLEEPING_GOLEMS.get(),
                DECISIONS.get(), INVENTORY_MUTATIONS.get());
    }

    public static record Snapshot(int activeOrders, int pausedOrders, int sleepingGolems,
                                  long decisions, long inventoryMutations) {
        public String summary() {
            return "active_orders=" + activeOrders + " paused_orders=" + pausedOrders
                    + " sleeping_golems=" + sleepingGolems + " decisions=" + decisions
                    + " inventory_mutations=" + inventoryMutations;
        }
    }
}

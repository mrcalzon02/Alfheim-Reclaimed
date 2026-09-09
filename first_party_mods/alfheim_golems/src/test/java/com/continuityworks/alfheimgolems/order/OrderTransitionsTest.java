package com.continuityworks.alfheimgolems.order;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class OrderTransitionsTest {
    @Test
    void carryingCargoCannotCancelIntoNothing() {
        assertFalse(OrderTransitions.canTransition(OrderState.CARRYING, OrderState.CANCELLED));
        assertTrue(OrderTransitions.canTransition(OrderState.CARRYING, OrderState.RETURNING_HOME));
        assertTrue(OrderTransitions.canTransition(OrderState.CARRYING, OrderState.PAUSED));
    }

    @Test
    void terminalStatesCannotRestart() {
        for (OrderState target : OrderState.values()) {
            assertFalse(OrderTransitions.canTransition(OrderState.COMPLETE, target));
            assertFalse(OrderTransitions.canTransition(OrderState.CANCELLED, target));
        }
    }

    @Test
    void nullAndInventedTransitionsFailClosed() {
        assertFalse(OrderTransitions.canTransition(null, OrderState.READY));
        assertFalse(OrderTransitions.canTransition(OrderState.DRAFT, null));
        assertFalse(OrderTransitions.canTransition(OrderState.DRAFT, OrderState.INSERTING));
    }
}

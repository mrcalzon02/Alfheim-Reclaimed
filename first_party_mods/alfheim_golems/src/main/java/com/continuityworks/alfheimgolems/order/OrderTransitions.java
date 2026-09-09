package com.continuityworks.alfheimgolems.order;

import java.util.EnumMap;
import java.util.EnumSet;
import java.util.Map;
import java.util.Set;

/** Closed transition graph. Packets and adapters cannot invent new order states. */
public final class OrderTransitions {
    private static final Map<OrderState, Set<OrderState>> ALLOWED = new EnumMap<>(OrderState.class);

    static {
        allow(OrderState.DRAFT, OrderState.READY, OrderState.CANCELLED);
        allow(OrderState.READY, OrderState.VALIDATING, OrderState.PAUSED, OrderState.CANCELLED);
        allow(OrderState.VALIDATING, OrderState.MOVING_TO_SOURCE, OrderState.PAUSED, OrderState.CANCELLED);
        allow(OrderState.MOVING_TO_SOURCE, OrderState.EXTRACTING, OrderState.PAUSED, OrderState.CANCELLED);
        allow(OrderState.EXTRACTING, OrderState.CARRYING, OrderState.PAUSED, OrderState.CANCELLED);
        allow(OrderState.CARRYING, OrderState.MOVING_TO_DESTINATION, OrderState.RETURNING_HOME, OrderState.PAUSED);
        allow(OrderState.MOVING_TO_DESTINATION, OrderState.INSERTING, OrderState.PAUSED);
        allow(OrderState.INSERTING, OrderState.WAITING_FOR_RESULT, OrderState.RETURNING_HOME,
                OrderState.COMPLETE, OrderState.PAUSED);
        allow(OrderState.WAITING_FOR_RESULT, OrderState.CARRYING, OrderState.RETURNING_HOME,
                OrderState.COMPLETE, OrderState.PAUSED);
        allow(OrderState.RETURNING_HOME, OrderState.COMPLETE, OrderState.PAUSED);
        allow(OrderState.PAUSED, OrderState.VALIDATING, OrderState.RETURNING_HOME, OrderState.CANCELLED);
        allow(OrderState.COMPLETE);
        allow(OrderState.CANCELLED);
    }

    private OrderTransitions() {}

    private static void allow(OrderState from, OrderState... to) {
        ALLOWED.put(from, to.length == 0 ? EnumSet.noneOf(OrderState.class) : EnumSet.of(to[0], to));
    }

    public static boolean canTransition(OrderState from, OrderState to) {
        return from != null && to != null && ALLOWED.getOrDefault(from, Set.of()).contains(to);
    }
}

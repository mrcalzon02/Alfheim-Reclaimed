package com.continuityworks.alfheimgolems.order;

public enum OrderState {
    DRAFT,
    READY,
    VALIDATING,
    MOVING_TO_SOURCE,
    EXTRACTING,
    CARRYING,
    MOVING_TO_DESTINATION,
    INSERTING,
    WAITING_FOR_RESULT,
    RETURNING_HOME,
    PAUSED,
    COMPLETE,
    CANCELLED
}

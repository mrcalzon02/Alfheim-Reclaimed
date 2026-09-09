package com.continuityworks.alfheimgolems.domain;

public enum Disposition {
    OWNED(true, true),
    WILD(false, true),
    SUMMONED(true, false);

    private final boolean requiresOwner;
    private final boolean persistent;

    Disposition(boolean requiresOwner, boolean persistent) {
        this.requiresOwner = requiresOwner;
        this.persistent = persistent;
    }

    public boolean requiresOwner() {
        return requiresOwner;
    }

    public boolean persistent() {
        return persistent;
    }
}

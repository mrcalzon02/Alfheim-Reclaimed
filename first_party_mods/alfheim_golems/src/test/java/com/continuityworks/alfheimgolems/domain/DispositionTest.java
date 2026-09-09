package com.continuityworks.alfheimgolems.domain;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class DispositionTest {
    @Test
    void summonedGolemsRequireOwnersAndAreNeverPersistent() {
        assertTrue(Disposition.SUMMONED.requiresOwner());
        assertFalse(Disposition.SUMMONED.persistent());
        assertFalse(Disposition.WILD.requiresOwner());
        assertTrue(Disposition.WILD.persistent());
        assertTrue(Disposition.OWNED.requiresOwner());
        assertTrue(Disposition.OWNED.persistent());
    }
}

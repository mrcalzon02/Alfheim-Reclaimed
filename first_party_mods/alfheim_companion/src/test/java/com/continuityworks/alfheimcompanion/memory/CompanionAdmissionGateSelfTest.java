package com.continuityworks.alfheimcompanion.memory;

import java.util.UUID;

/** Standalone Java 17 admission test; no Forge or Minecraft dependencies. */
public final class CompanionAdmissionGateSelfTest {
    private CompanionAdmissionGateSelfTest() {}

    private static void check(boolean okay, String message) {
        if (!okay) throw new AssertionError(message);
    }

    public static void main(String[] args) {
        UUID entity = UUID.randomUUID();
        UUID owner = UUID.randomUUID();
        UUID otherEntity = UUID.randomUUID();
        UUID otherOwner = UUID.randomUUID();
        CompanionAdmissionGate gate = new CompanionAdmissionGate();

        check(!gate.allows(entity, owner, null, null), "unreserved entity admitted");
        check(!gate.begin(null, owner), "null entity reservation");
        check(!gate.begin(entity, null), "null owner reservation");
        check(gate.begin(entity, owner), "valid reservation failed");
        check(!gate.begin(otherEntity, owner), "concurrent reservation accepted");
        check(gate.allows(entity, owner, null, null), "reserved entity rejected");
        check(!gate.allows(entity, otherOwner, null, null), "wrong owner admitted");
        check(!gate.allows(otherEntity, owner, null, null), "wrong UUID admitted");
        check(!gate.allows(null, owner, entity, owner), "null UUID admitted");
        check(!gate.allows(entity, null, entity, owner), "null owner admitted");

        // Existing matching entity may still reload during a staged new insertion.
        check(gate.allows(otherEntity, otherOwner, otherEntity, otherOwner),
                "committed entity reload rejected");
        boolean mismatchedEndRejected = false;
        try { gate.end(entity, otherOwner); }
        catch (IllegalStateException expected) { mismatchedEndRejected = true; }
        check(mismatchedEndRejected, "foreign caller ended reservation");
        check(gate.allows(entity, owner, null, null), "foreign end cleared reservation");

        gate.end(entity, owner);
        check(!gate.allows(entity, owner, null, null),
                "failed new entity remained approved after cancellation");
        check(gate.allows(entity, owner, entity, owner),
                "committed entity rejected during reload");
        check(!gate.allows(entity, otherOwner, entity, owner),
                "committed owner mismatch admitted");
        check(!gate.allows(otherEntity, owner, entity, owner),
                "mismatched committed UUID admitted");
        check(gate.begin(otherEntity, otherOwner), "retry admission impossible");
        gate.end(otherEntity, otherOwner);
        check(!gate.allows(otherEntity, otherOwner, null, null),
                "retry reservation remained open");
        System.out.println("COMPANION_ADMISSION_GATE_PASS: single-use transient reservation, owner checks, rejected-spawn retry, committed reload");
    }
}

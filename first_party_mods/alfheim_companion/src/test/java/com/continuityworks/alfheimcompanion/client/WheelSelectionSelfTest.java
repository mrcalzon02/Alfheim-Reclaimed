package com.continuityworks.alfheimcompanion.client;

/** Runnable with Java 17 and no Minecraft or third-party dependencies. */
public final class WheelSelectionSelfTest {
    private static final int ACTIONS = 8;
    private WheelSelectionSelfTest() {}

    private static void expect(int expected, double dx, double dy, int count) {
        int actual = WheelSelection.index(dx, dy, count, 28, 130);
        if (actual != expected)
            throw new AssertionError("expected " + expected + " but got " + actual
                    + " at (" + dx + ", " + dy + ") with " + count + " actions");
    }

    public static void main(String[] args) {
        for (int i = 0; i < ACTIONS; i++) {
            double angle = -Math.PI / 2.0 + i * (Math.PI * 2.0 / ACTIONS);
            expect(i, Math.cos(angle) * 82, Math.sin(angle) * 82, ACTIONS);
        }
        expect(-1, 0, 0, ACTIONS); // release in the safe centre
        expect(-1, 27, 0, ACTIONS); // inner dead zone
        expect(2, 28, 0, ACTIONS);  // first valid point
        expect(2, 130, 0, ACTIONS); // outer edge is still actionable
        expect(-1, 131, 0, ACTIONS); // off-wheel release must never send a command
        expect(2, 82, 0, ACTIONS);
        expect(0, 0, -82, ACTIONS);
        expect(4, 0, 82, ACTIONS);
        expect(6, -82, 0, ACTIONS);
        for (int i = 0; i < 6; i++) {
            double angle = -Math.PI / 2.0 + i * (Math.PI * 2.0 / 6);
            expect(i, Math.cos(angle) * 82, Math.sin(angle) * 82, 6);
        }
        int invalid = WheelSelection.index(Double.NaN, 0, 8, 28, 130);
        if (invalid != -1) throw new AssertionError("NaN pointer must cancel");
        if (WheelSelection.index(80, 0, 0, 28, 130) != -1)
            throw new AssertionError("zero actions must cancel");
        if (WheelSelection.index(80, 0, 8, 130, 28) != -1)
            throw new AssertionError("inverted radii must cancel");
        // The release pointer is authoritative, not the preceding animation frame's hover.
        expect(1, 58, -58, ACTIONS);
        expect(-1, 0, 0, ACTIONS);
        System.out.println("WHEEL_SELECTION_PASS: 8/6-sector layout, safe centre, outer limit, invalid pointer, release re-evaluation");
    }
}

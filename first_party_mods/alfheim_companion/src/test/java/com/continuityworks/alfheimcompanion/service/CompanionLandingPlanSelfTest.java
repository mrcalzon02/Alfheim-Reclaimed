package com.continuityworks.alfheimcompanion.service;

import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

/** Pure Java 17 regression for exhaustive, bounded summon candidates. */
public final class CompanionLandingPlanSelfTest {
    private CompanionLandingPlanSelfTest() {}

    public static void main(String[] args) {
        List<CompanionLandingPlan.Offset> offsets = CompanionLandingPlan.candidates();
        if (offsets.size() != 240) throw new AssertionError("expected 240 unique ring/height candidates");
        if (new HashSet<>(offsets).size() != offsets.size())
            throw new AssertionError("duplicate candidate wastes collision checks");
        Set<Integer> expectedHeights = Set.of(-2, -1, 0, 1, 2);
        Map<String, Set<Integer>> horizontal = new HashMap<>();
        int lastRadius = 0;
        for (CompanionLandingPlan.Offset point : offsets) {
            int radius = Math.max(Math.abs(point.dx()), Math.abs(point.dz()));
            if (radius < 1 || radius > CompanionLandingPlan.MAX_HORIZONTAL_RADIUS)
                throw new AssertionError("invalid ring: " + point);
            if (radius < lastRadius) throw new AssertionError("candidate order is not near-to-far");
            lastRadius = radius;
            horizontal.computeIfAbsent(point.dx() + "," + point.dz(), ignored -> new HashSet<>())
                    .add(point.dy());
        }
        if (horizontal.size() != 48) throw new AssertionError("missing horizontal candidates");
        for (Set<Integer> heights : horizontal.values()) {
            if (!heights.equals(expectedHeights)) throw new AssertionError("missing vertical alternatives");
        }
        try {
            offsets.clear();
            throw new AssertionError("candidate list must be immutable");
        } catch (UnsupportedOperationException expected) { }
        System.out.println("COMPANION_LANDING_PLAN_PASS: 240 unique, bounded, near-first, multi-height candidates");
    }
}

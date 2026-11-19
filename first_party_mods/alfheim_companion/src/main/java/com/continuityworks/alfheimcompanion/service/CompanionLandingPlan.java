package com.continuityworks.alfheimcompanion.service;

import java.util.ArrayList;
import java.util.List;

/** Bounded, duplicate-free candidate order for a safe companion landing. */
public final class CompanionLandingPlan {
    public static final int MAX_HORIZONTAL_RADIUS = 3;
    private static final int[] HEIGHT_OFFSETS = {0, 1, -1, 2, -2};
    private static final List<Offset> CANDIDATES = build();

    private CompanionLandingPlan() {}

    public record Offset(int dx, int dy, int dz) {}

    public static List<Offset> candidates() { return CANDIDATES; }

    private static List<Offset> build() {
        List<Offset> candidates = new ArrayList<>();
        for (int radius = 1; radius <= MAX_HORIZONTAL_RADIUS; radius++) {
            for (int dx = -radius; dx <= radius; dx++) {
                for (int dz = -radius; dz <= radius; dz++) {
                    if (Math.max(Math.abs(dx), Math.abs(dz)) != radius) continue;
                    for (int dy : HEIGHT_OFFSETS) candidates.add(new Offset(dx, dy, dz));
                }
            }
        }
        return List.copyOf(candidates);
    }
}

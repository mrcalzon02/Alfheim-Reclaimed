package com.continuityworks.alfheimcompanion.service;

import java.util.ArrayList;
import java.util.List;

/** Pure chunk-window difference planning; production applies the returned changes via Forge. */
public final class ChunkTicketDelta {
    private ChunkTicketDelta() {}

    public record Change(int x, int z, boolean add) {}

    /** Keep overlapping tickets; add entering edges before removing outgoing edges. */
    public static List<Change> moving(int oldX, int oldZ, int newX, int newZ, int radius) {
        if (radius < 0 || radius > 8) throw new IllegalArgumentException("radius must be in 0..8");
        validateCenter(oldX, oldZ, radius);
        validateCenter(newX, newZ, radius);
        List<Change> changes = new ArrayList<>();
        for (int dx = -radius; dx <= radius; dx++) {
            for (int dz = -radius; dz <= radius; dz++) {
                int x = newX + dx;
                int z = newZ + dz;
                if (!inside(x, z, oldX, oldZ, radius)) changes.add(new Change(x, z, true));
            }
        }
        for (int dx = -radius; dx <= radius; dx++) {
            for (int dz = -radius; dz <= radius; dz++) {
                int x = oldX + dx;
                int z = oldZ + dz;
                if (!inside(x, z, newX, newZ, radius)) changes.add(new Change(x, z, false));
            }
        }
        return List.copyOf(changes);
    }

    private static void validateCenter(int x, int z, int radius) {
        if ((long) x - radius < Integer.MIN_VALUE || (long) x + radius > Integer.MAX_VALUE
                || (long) z - radius < Integer.MIN_VALUE || (long) z + radius > Integer.MAX_VALUE)
            throw new IllegalArgumentException("chunk window would overflow coordinate range");
    }

    private static boolean inside(int x, int z, int centerX, int centerZ, int radius) {
        return Math.abs((long) x - centerX) <= radius && Math.abs((long) z - centerZ) <= radius;
    }
}

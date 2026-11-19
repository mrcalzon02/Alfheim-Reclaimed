package com.continuityworks.alfheimcompanion.service;

import java.util.HashSet;
import java.util.List;
import java.util.Set;

/** Runnable with Java 17 and without any Minecraft/Forge dependencies. */
public final class ChunkTicketDeltaSelfTest {
    private ChunkTicketDeltaSelfTest() {}

    public static void main(String[] args) {
        check(0, 0, 0, 0, 0, 0);
        check(0, 0, 1, 0, 3, 3);
        check(0, 0, 1, 1, 5, 5);
        check(0, 0, 3, 0, 9, 9);
        check(-7, -11, -8, -10, 5, 5);
        check(5, 5, 3, 5, 6, 6);
        check(0, 0, 20, -20, 9, 9);
        boolean rejectsOverflow = false;
        try { ChunkTicketDelta.moving(Integer.MIN_VALUE, 0, Integer.MAX_VALUE, 0, 1); }
        catch (IllegalArgumentException expected) { rejectsOverflow = true; }
        if (!rejectsOverflow) throw new AssertionError("unrepresentable chunk window accepted");
        boolean rejectsBadRadius = false;
        try { ChunkTicketDelta.moving(0, 0, 1, 0, -1); }
        catch (IllegalArgumentException expected) { rejectsBadRadius = true; }
        if (!rejectsBadRadius) throw new AssertionError("invalid radius accepted");
        System.out.println("CHUNK_TICKET_DELTA_PASS: stationary, adjacent, diagonal, distant, negative and extreme coordinate transitions");
    }

    private static void check(int ox, int oz, int nx, int nz, int adds, int removes) {
        Set<String> active = square(ox, oz);
        Set<String> expected = square(nx, nz);
        Set<String> overlap = new HashSet<>(active);
        overlap.retainAll(expected);
        List<ChunkTicketDelta.Change> changes = ChunkTicketDelta.moving(ox, oz, nx, nz, 1);
        int addCount = 0, removeCount = 0;
        boolean beganRemoving = false;
        for (ChunkTicketDelta.Change change : changes) {
            String key = change.x() + ":" + change.z();
            if (overlap.contains(key)) throw new AssertionError("modified an overlapping ticket " + key);
            if (change.add()) {
                if (beganRemoving) throw new AssertionError("new tickets must be installed first");
                if (!active.add(key)) throw new AssertionError("duplicate addition " + key);
                addCount++;
            } else {
                beganRemoving = true;
                if (!active.remove(key)) throw new AssertionError("removal of absent ticket " + key);
                removeCount++;
            }
        }
        if (addCount != adds || removeCount != removes)
            throw new AssertionError("unexpected changes " + addCount + "/" + removeCount +
                    " vs " + adds + "/" + removes);
        if (!active.equals(expected) || active.size() != 9)
            throw new AssertionError("incorrect final ticket set: " + active + " vs " + expected);
    }

    private static Set<String> square(int cx, int cz) {
        Set<String> s = new HashSet<>();
        for (int dx = -1; dx <= 1; dx++)
            for (int dz = -1; dz <= 1; dz++) s.add((cx + dx) + ":" + (cz + dz));
        return s;
    }
}

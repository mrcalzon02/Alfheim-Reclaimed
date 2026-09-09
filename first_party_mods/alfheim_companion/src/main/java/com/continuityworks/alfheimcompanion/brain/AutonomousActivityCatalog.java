package com.continuityworks.alfheimcompanion.brain;

import com.continuityworks.alfheimcompanion.memory.BehaviorPreset;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

/** Pure scoring policy for the currently implemented, non-destructive autonomous activities. */
public final class AutonomousActivityCatalog {
    private AutonomousActivityCatalog() {}

    public static List<AutonomousActivityOption> optionsFor(BehaviorPreset preset, int nutrition,
                                                             int stamina, int claimCount,
                                                             AutonomousActivityKind previous) {
        BehaviorPreset policy = preset == null ? BehaviorPreset.BALANCED : preset;
        AutonomousActivityKind last = previous == null ? AutonomousActivityKind.NONE : previous;
        if (nutrition <= 6 || stamina <= policy.recoveryFloor()) {
            return List.of(option("RECOVER_AT_BASE", AutonomousActivityKind.RECOVER_AT_BASE, 100,
                    "needs below preset recovery floor"));
        }

        List<AutonomousActivityOption> options = new ArrayList<>();
        options.add(option("PATROL_CLAIMS", AutonomousActivityKind.PATROL_CLAIMS,
                score(28 + policy.combatWeight() / 2 + Math.min(10, claimCount),
                        last == AutonomousActivityKind.PATROL_CLAIMS),
                "verify delegated district boundaries"));
        options.add(option("SURVEY_DISTRICT", AutonomousActivityKind.SURVEY_DISTRICT,
                score(30 + policy.questWeight() / 2 + Math.min(10, claimCount),
                        last == AutonomousActivityKind.SURVEY_DISTRICT),
                "refresh terrain observations for later work"));
        options.add(option("INSPECT_BASE", AutonomousActivityKind.INSPECT_BASE,
                score(30 + policy.buildWeight() / 2,
                        last == AutonomousActivityKind.INSPECT_BASE),
                "inspect the established operating anchor"));
        options.add(option("RECOVER_AT_BASE", AutonomousActivityKind.RECOVER_AT_BASE,
                score(15 + policy.recoveryFloor() / 2,
                        last == AutonomousActivityKind.RECOVER_AT_BASE),
                "return to the anchor for a quiet interval"));
        options.sort(Comparator.comparingInt(AutonomousActivityOption::value).reversed()
                .thenComparing(AutonomousActivityOption::id));
        return List.copyOf(options);
    }

    public static AutonomousActivityOption require(String id, List<AutonomousActivityOption> options) {
        return options.stream().filter(option -> option.id().equals(id)).findFirst()
                .orElseThrow(() -> new IllegalArgumentException("activity outside offered menu"));
    }

    private static int score(int value, boolean repeated) {
        return Math.max(0, Math.min(100, value - (repeated ? 35 : 0)));
    }

    private static AutonomousActivityOption option(String id, AutonomousActivityKind kind,
                                                    int value, String reason) {
        return new AutonomousActivityOption(id, kind, value, reason, false, false);
    }
}

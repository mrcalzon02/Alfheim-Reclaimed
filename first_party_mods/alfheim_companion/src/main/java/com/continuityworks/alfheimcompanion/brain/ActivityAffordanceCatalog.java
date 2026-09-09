package com.continuityworks.alfheimcompanion.brain;

import java.util.ArrayList;
import java.util.List;

/** Builds the complete legal action menu from trusted state and the selected preference preset. */
public final class ActivityAffordanceCatalog {
    private ActivityAffordanceCatalog() {}

    public static List<ActionAffordance> optionsFor(BrainSnapshot snapshot) {
        if (!snapshot.question().isBlank()) {
            return List.of(action("ANSWER_ONLY", "answer from offered evidence", BrainDirective.ADVISE,
                    0, "answer_question", ActivityBaseline.COMPANIONSHIP, false));
        }

        List<ActionAffordance> options = new ArrayList<>();
        BrainSnapshot.Threat nearest = snapshot.threats().isEmpty() ? null : snapshot.threats().get(0);
        if (nearest != null && (snapshot.ownerHealthPercent() <= 25 || snapshot.companionHealthPercent() <= 25))
            options.add(action("RETREAT_TO_OWNER", "retreat to the owner safe point", BrainDirective.RETREAT,
                    nearest.entityId(), "retreat_to_owner_safe_point", ActivityBaseline.SAFETY, false));
        if (nearest != null)
            options.add(action("DEFEND_NEAREST", "defend the owner from the nearest verified threat",
                    BrainDirective.DEFEND, nearest.entityId(), "defend_owner",
                    ActivityBaseline.OWNER_PROTECTION, false));

        int recoveryFloor = recoveryFloor(snapshot.behaviorPreset());
        if (snapshot.companionHealthPercent() <= recoveryFloor || snapshot.nutrition() <= 6
                || snapshot.stamina() <= recoveryFloor)
            options.add(action("RECOVER_NEEDS", "pause in safety to recover bounded needs", BrainDirective.WAIT,
                    0, "recover_needs", ActivityBaseline.RECOVERY, false));

        if (!snapshot.basePhase().isBlank() && !snapshot.basePhase().equals("NONE")
                && !snapshot.basePhase().equals("MAINTAINING") && !snapshot.basePhase().equals("PAUSED"))
            options.add(action("ADVANCE_BASE", "continue the registered base objective phase",
                    BrainDirective.EXECUTE_TASK, 0, "base:" + snapshot.basePhase().toLowerCase(),
                    ActivityBaseline.EXPLICIT_OBJECTIVE, true));
        else if (!snapshot.activeTask().isBlank())
            options.add(action("CONTINUE_TASK", "continue the explicit owner task", BrainDirective.EXECUTE_TASK,
                    0, snapshot.activeTask(), ActivityBaseline.EXPLICIT_OBJECTIVE,
                    snapshot.activeTask().toLowerCase().contains("build")));

        if (snapshot.basePhase().equals("MAINTAINING"))
            options.add(action("GUARD_BASE", "remain near the established operating anchor",
                    BrainDirective.WAIT, 0, "guard_base", ActivityBaseline.BASE_STEWARDSHIP, false));
        options.add(action("FOLLOW_OWNER", "travel with the owner", BrainDirective.FOLLOW, 0,
                "follow_owner", ActivityBaseline.COMPANIONSHIP, false));
        options.add(action("HOLD_POSITION", "wait without changing the world", BrainDirective.WAIT, 0,
                "wait", ActivityBaseline.COMPANIONSHIP, false));
        return List.copyOf(options.subList(0, Math.min(6, options.size())));
    }

    public static ActionAffordance require(String id, BrainSnapshot snapshot) {
        return optionsFor(snapshot).stream().filter(option -> option.id().equals(id)).findFirst()
                .orElseThrow(() -> new IllegalArgumentException("model selected an action outside the offered menu"));
    }

    private static int recoveryFloor(String preset) {
        return switch (preset == null ? "" : preset) {
            case "steward" -> 40;
            case "warden", "artisan" -> 30;
            default -> 25;
        };
    }

    private static ActionAffordance action(String id, String label, BrainDirective directive, int target,
                                           String task, ActivityBaseline baseline, boolean approval) {
        return new ActionAffordance(id, label, directive, target, task, baseline, approval);
    }
}

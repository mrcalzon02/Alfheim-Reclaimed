package com.continuityworks.alfheimcompanion.brain;

import com.continuityworks.alfheimcompanion.personality.DialogueBank;
import java.util.concurrent.CompletableFuture;
import java.util.Optional;

public final class RuleBasedTinyBrainEngine implements TinyBrainEngine {
    @Override
    public String engineId() {
        return "rules-v1";
    }

    @Override
    public CompletableFuture<BrainDecision> plan(BrainSnapshot snapshot) {
        BrainDecision decision;
        if (snapshot.ownerHealthPercent() <= 25 && !snapshot.threats().isEmpty()) {
            decision = new BrainDecision(snapshot.requestId(), BrainDirective.RETREAT,
                    snapshot.threats().get(0).entityId(), "retreat_to_owner_safe_point",
                    DialogueBank.line(DialogueBank.Moment.RETREAT, snapshot.requestId()));
        } else if (!snapshot.threats().isEmpty()) {
            decision = new BrainDecision(snapshot.requestId(), BrainDirective.DEFEND,
                    snapshot.threats().get(0).entityId(), "defend_owner",
                    DialogueBank.line(DialogueBank.Moment.DEFEND, snapshot.requestId()));
        } else if (!snapshot.activeTask().isBlank()) {
            decision = new BrainDecision(snapshot.requestId(), BrainDirective.EXECUTE_TASK,
                    0, snapshot.activeTask(), "I will continue our work.");
        } else {
            decision = new BrainDecision(snapshot.requestId(), BrainDirective.FOLLOW,
                    0, "follow_owner", "I am with you.");
        }
        return CompletableFuture.completedFuture(decision);
    }

    @Override
    public CompletableFuture<Optional<String>> reflect(AmbientSnapshot snapshot) {
        String line = switch (snapshot.timeOfDay()) {
            case "night" -> "The stars make even this road feel a little like Alfheim.";
            case "dawn" -> "A bright hour for beginning careful work.";
            default -> "I am keeping watch while we travel.";
        };
        return CompletableFuture.completedFuture(Optional.of(line));
    }
}

package com.continuityworks.alfheimcompanion.brain.local;

import com.continuityworks.alfheimcompanion.brain.BrainSnapshot;
import com.continuityworks.alfheimcompanion.brain.QuestContext;
import com.continuityworks.alfheimcompanion.brain.SkillChoice;
import com.continuityworks.alfheimcompanion.brain.ActivityAffordanceCatalog;

import com.continuityworks.alfheimcompanion.conversation.ConversationCatalog;

/** Builds a compact evidence packet; it never serializes a world object or an unrestricted registry. */
public final class InferencePrompt {
    private static final int MAX_USER_CHARS = 1200;

    private InferencePrompt() {}

    public static String system(boolean allowFreeform) {
        return "You are the bounded planner for one elven Minecraft companion. Choose only IDs present "
                + "in the evidence. Never invent a quest, fact, target, item, mod rule, or skill. Return one "
                + "JSON object only: {\"directive\":\"ADVISE\",\"target\":0,"
                + "\"action\":\"ANSWER_ONLY\",\"skill\":\"\"," 
                + "\"response\":\"NEED_MORE_CONTEXT\",\"fact\":\"\",\"say\":\"\"}. "
                + "The action value must be one action_options ID. Java ignores directive and target and derives them from action. "
                + "The response value must be one response_options ID from the evidence."
                + (allowFreeform ? " Use say only with FREEFORM_GROUNDED and only from evidence."
                : ". The say field must be empty; free-form wording is disabled.");
    }

    public static String user(BrainSnapshot snapshot, boolean allowFreeform) {
        StringBuilder out = new StringBuilder(MAX_USER_CHARS);
        append(out, "question=", snapshot.question());
        append(out, "action_options=", ActivityAffordanceCatalog.optionsFor(snapshot).stream()
                .map(option -> option.id() + ":" + option.baseline()
                        + (option.ownerApprovalRequired() ? ":approval" : "")).toList());
        append(out, "response_options=", ConversationCatalog.optionsFor(snapshot, allowFreeform));
        append(out, "task=", snapshot.activeTask());
        append(out, "base_phase=", snapshot.basePhase());
        append(out, "behavior_preset=", snapshot.behaviorPreset());
        append(out, "companion=", snapshot.companionName());
        append(out, "dimension=", snapshot.dimensionId());
        append(out, "biome=", snapshot.biome());
        append(out, "conditions=", snapshot.timeOfDay() + "," + snapshot.weather());
        append(out, "mode=", snapshot.mode());
        append(out, "owner_health=", snapshot.ownerHealthPercent() + "%");
        append(out, "companion_health=", snapshot.companionHealthPercent() + "%");
        append(out, "needs=", "nutrition " + snapshot.nutrition() + "/20,stamina " + snapshot.stamina() + "/100");
        append(out, "personality=", snapshot.personality());
        append(out, "combat_profile=", snapshot.combatProfile());
        for (BrainSnapshot.Threat threat : snapshot.threats()) {
            append(out, "threat=", threat.entityId() + "," + threat.entityType() + ",distance_sq=" + threat.distanceSquared());
        }
        for (QuestContext quest : snapshot.quests()) {
            append(out, "quest=", quest.id() + "," + quest.name() + "," + quest.status() + ",goal=" + quest.goal());
            for (String objective : quest.objectives()) append(out, "objective=", objective);
            for (String missing : quest.missingIngredients()) append(out, "missing=", missing);
        }
        for (SkillChoice skill : snapshot.skillChoices()) {
            append(out, "skill=", skill.id() + "," + skill.name() + ",role=" + skill.role()
                    + ",directive=" + skill.directive()
                    + ",ready=" + skill.ready() + ",cost=" + skill.cost() + " " + skill.resource()
                    + ",constraint=" + skill.constraint());
        }
        snapshot.recalledFacts().entrySet().stream().limit(8)
                .forEach(entry -> append(out, "fact=", entry.getKey() + ":" + entry.getValue()));
        return out.toString();
    }

    private static void append(StringBuilder out, String prefix, Object raw) {
        if (out.length() >= MAX_USER_CHARS) return;
        String value = String.valueOf(raw == null ? "" : raw).replace('\n', ' ')
                .replace('\r', ' ').replace('|', '/').strip();
        int remaining = MAX_USER_CHARS - out.length() - prefix.length() - 1;
        if (remaining <= 0) return;
        out.append(prefix).append(value, 0, Math.min(value.length(), remaining)).append('\n');
    }
}

package com.continuityworks.alfheimcompanion.conversation;

import com.continuityworks.alfheimcompanion.brain.BrainSnapshot;
import com.continuityworks.alfheimcompanion.brain.QuestContext;
import com.continuityworks.alfheimcompanion.brain.SkillChoice;
import com.continuityworks.alfheimcompanion.brain.ActivityAffordanceCatalog;

import java.util.Map;
import java.util.List;
import java.util.ArrayList;
import java.util.Optional;
import static com.continuityworks.alfheimcompanion.conversation.ConversationResponse.*;

/** Deterministic response assembly for the small-model conversation tree. */
public final class ConversationCatalog {
    private ConversationCatalog() {}

    public static String render(ConversationResponse response, BrainSnapshot snapshot,
                                String selectedSkillId, String selectedFactKey,
                                String boundedFreeform) {
        Optional<QuestContext> quest = snapshot.quests().stream().findFirst();
        Optional<SkillChoice> skill = snapshot.skillChoices().stream()
                .filter(choice -> choice.id().equals(selectedSkillId)).findFirst();
        return switch (response) {
            case ACKNOWLEDGE_TASK -> choose(snapshot, "I understand. I will weigh the safe choices before we proceed.",
                    "Understood. I will compare only the choices the world has actually given me.",
                    "I have it. I will keep the plan bounded and verify each step.");
            case CONTINUE_TASK -> snapshot.activeTask().isBlank() ? taskNone(snapshot)
                    : choose(snapshot, "I will continue " + readableTask(snapshot.activeTask()) + ".",
                    "Our present work remains " + readableTask(snapshot.activeTask()) + ". I will carry on.",
                    "I have not lost the thread: " + readableTask(snapshot.activeTask()) + ".");
            case QUEST_SUMMARY -> quest.map(value -> value.name() + " is " + value.status().toLowerCase()
                    + ". " + value.goal()).orElse("I cannot see a relevant quest in the current ledger.");
            case QUEST_OBJECTIVE -> quest.map(value -> value.objectives().isEmpty()
                    ? "I see no unfinished objective listed for " + value.name() + "."
                    : "The next recorded objective for " + value.name() + " is " + value.objectives().get(0) + ".")
                    .orElse("I cannot see a relevant quest objective.");
            case QUEST_MISSING_ITEMS -> quest.map(value -> value.missingIngredients().isEmpty()
                    ? "We already have the listed materials for " + value.name() + "."
                    : "For " + value.name() + ", we still need " + String.join(", ", value.missingIngredients()) + ".")
                    .orElse("I cannot see a relevant quest in the current ledger.");
            case QUEST_MATERIALS_READY -> quest.map(value -> value.missingIngredients().isEmpty()
                    ? "The recorded materials for " + value.name() + " are ready."
                    : "The materials are not complete; we still need " + String.join(", ", value.missingIngredients()) + ".")
                    .orElse("I cannot verify the quest materials.");
            case QUEST_BLOCKED -> quest.map(value -> value.missingIngredients().isEmpty()
                    ? "The ledger shows no material shortage for " + value.name() + "; check its next objective."
                    : value.name() + " is presently blocked by " + String.join(", ", value.missingIngredients()) + ".")
                    .orElse("I cannot identify a verified blocker for that quest.");
            case QUEST_COMPLETE -> quest.map(value -> value.name() + " is complete.")
                    .orElse("I cannot confirm that quest's completion.");
            case SKILL_RECOMMENDATION -> skill.map(value -> "I recommend " + value.name() + " for "
                    + value.role() + ".").orElse("I do not have a validated MMO skill choice for that situation.");
            case SKILL_NOT_READY -> skill.map(value -> value.name() + " is not ready: " + value.constraint() + ".")
                    .orElse("That skill is not in my validated choices.");
            case SKILL_COST -> skill.map(value -> value.cost() == 0
                    ? value.name() + " has no recorded resource cost."
                    : value.name() + " costs " + value.cost() + " " + value.resource() + ".")
                    .orElse("I do not have a validated skill cost to report.");
            case SKILL_CONSTRAINT -> skill.map(value -> value.name() + " requires " + value.constraint() + ".")
                    .orElse("I do not have a validated skill constraint to report.");
            case SKILL_NO_CANDIDATE -> "No executable MMO skill has been offered for this companion and situation.";
            case STATUS_SUMMARY -> "My combat profile is " + blankAs(snapshot.combatProfile(), "not connected")
                    + (snapshot.activeTask().isBlank() ? ", and I have no active task."
                    : ", and my task is " + readableTask(snapshot.activeTask()) + ".");
            case TASK_SUMMARY -> snapshot.activeTask().isBlank() ? taskNone(snapshot)
                    : "My current task is " + readableTask(snapshot.activeTask()) + ".";
            case THREAT_SUMMARY -> snapshot.threats().isEmpty() ? "I see no nearby hostile threat in my bounded scan."
                    : "I see " + snapshot.threats().size() + " nearby threat"
                    + (snapshot.threats().size() == 1 ? "" : "s") + "; the nearest is "
                    + snapshot.threats().get(0).entityType() + ".";
            case COMPANION_WELLBEING -> choose(snapshot,
                    "I am at " + snapshot.companionHealthPercent() + "% health, with " + snapshot.nutrition()
                            + "/20 nutrition and " + snapshot.stamina() + "/100 stamina.",
                    "My condition is " + snapshot.companionHealthPercent() + "% health, " + snapshot.nutrition()
                            + "/20 fed, and " + snapshot.stamina() + "/100 rested.");
            case OWNER_WELLBEING -> "You are at " + snapshot.ownerHealthPercent()
                    + "% health in my latest verified view.";
            case LOCATION_SUMMARY -> "We are in " + readableId(snapshot.biome()) + " within "
                    + readableId(snapshot.dimensionId()) + ".";
            case CONDITIONS_SUMMARY -> "It is " + snapshot.timeOfDay() + " with " + snapshot.weather()
                    + " conditions in " + readableId(snapshot.biome()) + ".";
            case KNOWN_FACT -> knownFact(snapshot.recalledFacts(), selectedFactKey)
                    .orElse("I do not have that fact in my bounded memory.");
            case GREETING -> choose(snapshot, "Hello. I am listening.", "Well met. What shall we consider?",
                    "I am here, and the path is quiet enough to talk.");
            case GRATITUDE -> choose(snapshot, "Gladly.", "You are welcome.", "Of course. We share the road.");
            case SELF_INTRODUCTION -> "I am " + snapshot.companionName()
                    + ", your bonded elven companion and careful witness to our work.";
            case CAPABILITIES -> "I can follow, guard, defend, retreat, handle bounded item tasks, advise on crafting and quests, and establish an approved base in stages.";
            case BASE_STATUS -> snapshot.basePhase().equals("NONE")
                    ? "I do not have a base objective yet."
                    : "My base objective is in the " + readableId(snapshot.basePhase()) + " phase.";
            case BASE_NEXT_STEP -> "The next base step is " + baseNextStep(snapshot.basePhase()) + ".";
            case BEHAVIOR_PRESET -> "My current behavior preset is " + readableId(snapshot.behaviorPreset())
                    + "; it changes preferences, never safety or permission rules.";
            case APPROVAL_BOUNDARY -> "I may survey and plan autonomously, but every construction proposal requires your approval before any block changes.";
            case ACTIVITY_OPTIONS -> "My legal choices here are " + String.join(", ",
                    ActivityAffordanceCatalog.optionsFor(snapshot).stream()
                            .map(option -> readableId(option.id())).toList()) + ".";
            case MEMORY_UNAVAILABLE -> "I do not hold that in my bounded memory. Tell me directly, and I can remember a concise fact.";
            case LORE_BOUNDARY -> "I can answer only from the quest ledger, verified modpack context, and memories available to me here.";
            case NEED_MORE_CONTEXT -> "I do not have enough verified quest or modpack context to answer that yet.";
            case RETREAT_WARNING -> "We should yield this ground and recover before committing to another exchange.";
            case DEFEND_WARNING -> "I will hold the nearest threat away from you.";
            case FOLLOW_ACKNOWLEDGEMENT -> "I am with you.";
            case WAIT_ACKNOWLEDGEMENT -> "I will keep watch here.";
            case FREEFORM_GROUNDED -> limit(boundedFreeform, 120);
        };
    }

    /** Narrows the model's template menu to contextually legal responses. */
    public static List<ConversationResponse> optionsFor(BrainSnapshot snapshot, boolean allowFreeform) {
        List<ConversationResponse> options = new ArrayList<>(List.of(NEED_MORE_CONTEXT,
                STATUS_SUMMARY, TASK_SUMMARY, COMPANION_WELLBEING, OWNER_WELLBEING,
                LOCATION_SUMMARY, CONDITIONS_SUMMARY, KNOWN_FACT, MEMORY_UNAVAILABLE,
                LORE_BOUNDARY, GREETING, GRATITUDE, SELF_INTRODUCTION, CAPABILITIES,
                BASE_STATUS, BASE_NEXT_STEP, BEHAVIOR_PRESET, APPROVAL_BOUNDARY, ACTIVITY_OPTIONS));
        if (!snapshot.activeTask().isBlank()) options.addAll(List.of(ACKNOWLEDGE_TASK, CONTINUE_TASK));
        if (!snapshot.quests().isEmpty()) options.addAll(List.of(QUEST_SUMMARY, QUEST_OBJECTIVE,
                QUEST_MISSING_ITEMS, QUEST_MATERIALS_READY, QUEST_BLOCKED, QUEST_COMPLETE));
        if (snapshot.skillChoices().isEmpty()) options.add(SKILL_NO_CANDIDATE);
        else options.addAll(List.of(SKILL_RECOMMENDATION, SKILL_NOT_READY, SKILL_COST, SKILL_CONSTRAINT));
        if (!snapshot.threats().isEmpty()) options.addAll(List.of(THREAT_SUMMARY, RETREAT_WARNING, DEFEND_WARNING));
        if (allowFreeform) options.add(FREEFORM_GROUNDED);
        return List.copyOf(options);
    }

    private static Optional<String> knownFact(Map<String, String> facts, String key) {
        if (key == null || key.isBlank()) return Optional.empty();
        String value = facts.get(key);
        return value == null ? Optional.empty() : Optional.of(key.replace('_', ' ') + " is " + limit(value, 80) + ".");
    }

    private static String readableTask(String task) {
        return limit(task.replace('|', ' ').replace('_', ' '), 80);
    }

    private static String readableId(String value) {
        if (value == null || value.isBlank()) return "an unknown place";
        int separator = value.indexOf(':');
        String tail = separator >= 0 ? value.substring(separator + 1) : value;
        return limit(tail.replace('_', ' '), 64);
    }

    private static String taskNone(BrainSnapshot snapshot) {
        return choose(snapshot, "I have no unfinished task.", "My hands are free at present.",
                "No task is currently bound to our ledger.");
    }

    private static String baseNextStep(String phase) {
        return switch (phase == null ? "NONE" : phase) {
            case "SURVEY" -> "a dry, sufficiently level, claim-safe site survey";
            case "PROPOSING" -> "generation and validation of a bounded proposal";
            case "AWAITING_APPROVAL" -> "your explicit blueprint approval or rejection";
            case "BUILDING" -> "claim-checked, inventory-backed placement of the approved shell";
            case "FURNISHING" -> "a separately approved functional furnishing proposal";
            case "MAINTAINING" -> "guarding the anchor and proposing future repairs before changing it";
            case "PAUSED" -> "resolving the reported blocker or choosing a new site";
            default -> "an explicit request to establish a base";
        };
    }

    private static String choose(BrainSnapshot snapshot, String... variants) {
        int index = Math.floorMod(Long.hashCode(snapshot.requestId()), variants.length);
        return variants[index];
    }

    private static String blankAs(String value, String fallback) {
        return value == null || value.isBlank() ? fallback : limit(value, 90);
    }

    private static String limit(String value, int maximum) {
        if (value == null) return "";
        String clean = value.replace('\n', ' ').replace('\r', ' ').strip();
        return clean.length() <= maximum ? clean : clean.substring(0, maximum);
    }
}

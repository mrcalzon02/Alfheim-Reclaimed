package com.continuityworks.alfheimcompanion.conversation;

import com.continuityworks.alfheimcompanion.brain.BrainDecision;
import com.continuityworks.alfheimcompanion.brain.BrainDirective;
import com.continuityworks.alfheimcompanion.brain.BrainSnapshot;
import com.continuityworks.alfheimcompanion.brain.SkillChoice;

import java.util.Locale;
import java.util.Optional;

/** Resolves high-confidence conversation branches without invoking inference. */
public final class DeterministicConversationRouter {
    private DeterministicConversationRouter() {}

    public static Optional<BrainDecision> route(BrainSnapshot snapshot) {
        if (snapshot.question().isBlank()) return Optional.empty();
        String question = snapshot.question().toLowerCase(Locale.ROOT).replaceAll("[^a-z0-9:_ ]", " ")
                .replaceAll("\\s+", " ").strip();
        ConversationResponse response = null;
        String skill = "";
        if (question.matches("(hi|hello|hey|greetings|good (morning|evening))")) response = ConversationResponse.GREETING;
        else if (containsAny(question, "thank you", "thanks", "much appreciated")) response = ConversationResponse.GRATITUDE;
        else if (containsAny(question, "who are you", "what are you")) response = ConversationResponse.SELF_INTRODUCTION;
        else if (containsAny(question, "what can you do", "how can you help", "your capabilities")) response = ConversationResponse.CAPABILITIES;
        else if (containsAny(question, "next base step", "what happens next with the base", "base next")) response = ConversationResponse.BASE_NEXT_STEP;
        else if (containsAny(question, "base status", "your base", "our base")) response = ConversationResponse.BASE_STATUS;
        else if (containsAny(question, "behavior preset", "your preset", "how are you configured")) response = ConversationResponse.BEHAVIOR_PRESET;
        else if (containsAny(question, "need my approval", "build without approval", "construction permission")) response = ConversationResponse.APPROVAL_BOUNDARY;
        else if (containsAny(question, "what can you choose", "available actions", "activity options")) response = ConversationResponse.ACTIVITY_OPTIONS;
        else if (containsAny(question, "where are we", "what biome", "our location")) response = ConversationResponse.LOCATION_SUMMARY;
        else if (containsAny(question, "what time", "weather", "conditions here")) response = ConversationResponse.CONDITIONS_SUMMARY;
        else if (containsAny(question, "how are you", "your health", "your stamina", "are you hungry")) response = ConversationResponse.COMPANION_WELLBEING;
        else if (containsAny(question, "my health", "how hurt am i", "am i hurt")) response = ConversationResponse.OWNER_WELLBEING;
        else if (containsAny(question, "what are you doing", "current task", "our task")) response = ConversationResponse.TASK_SUMMARY;
        else if (question.contains("quest") && containsAny(question, "missing", "need", "materials", "ingredients"))
            response = snapshot.quests().stream().findFirst().map(quest -> quest.missingIngredients().isEmpty()
                    ? ConversationResponse.QUEST_MATERIALS_READY : ConversationResponse.QUEST_MISSING_ITEMS)
                    .orElse(ConversationResponse.NEED_MORE_CONTEXT);
        else if (question.contains("quest") && containsAny(question, "objective", "goal", "next")) response = ConversationResponse.QUEST_OBJECTIVE;
        else if (question.contains("quest") && containsAny(question, "blocked", "stuck", "cannot progress")) response = ConversationResponse.QUEST_BLOCKED;
        else if (question.contains("quest") && containsAny(question, "status", "current", "progress")) response = ConversationResponse.QUEST_SUMMARY;
        else if (containsAny(question, "nearby threat", "what is attacking", "enemies nearby")) response = ConversationResponse.THREAT_SUMMARY;
        else if (containsAny(question, "skill", "ability", "spell")) {
            Optional<SkillChoice> candidate = snapshot.skillChoices().stream().filter(SkillChoice::ready).findFirst()
                    .or(() -> snapshot.skillChoices().stream().findFirst());
            skill = candidate.map(SkillChoice::id).orElse("");
            if (candidate.isEmpty()) response = ConversationResponse.SKILL_NO_CANDIDATE;
            else if (containsAny(question, "cost", "mana", "energy", "resource")) response = ConversationResponse.SKILL_COST;
            else if (containsAny(question, "ready", "can use", "requirement", "requires"))
                response = candidate.get().ready() ? ConversationResponse.SKILL_CONSTRAINT : ConversationResponse.SKILL_NOT_READY;
            else response = ConversationResponse.SKILL_RECOMMENDATION;
        }
        if (response == null) return Optional.empty();
        String dialogue = ConversationCatalog.render(response, snapshot, skill, "", "");
        return Optional.of(new BrainDecision(snapshot.requestId(), BrainDirective.ADVISE, 0,
                "answer_question", skill, response.name(), dialogue));
    }

    private static boolean containsAny(String text, String... needles) {
        for (String needle : needles) if (text.contains(needle)) return true;
        return false;
    }
}

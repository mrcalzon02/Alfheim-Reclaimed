package com.continuityworks.alfheimcompanion.brain.local;

import com.continuityworks.alfheimcompanion.brain.BrainDecision;
import com.continuityworks.alfheimcompanion.brain.BrainDirective;
import com.continuityworks.alfheimcompanion.brain.BrainSnapshot;
import com.continuityworks.alfheimcompanion.brain.SkillChoice;
import com.continuityworks.alfheimcompanion.brain.ActionAffordance;
import com.continuityworks.alfheimcompanion.brain.ActivityAffordanceCatalog;
import com.continuityworks.alfheimcompanion.conversation.ConversationCatalog;
import com.continuityworks.alfheimcompanion.conversation.ConversationResponse;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import java.util.Locale;

/** Fail-closed parser and allow-list validator for untrusted model output. */
public final class InferenceResponseParser {
    private InferenceResponseParser() {}

    public static BrainDecision parse(String output, BrainSnapshot snapshot, boolean allowFreeform) {
        JsonObject json = objectFrom(output);
        String actionId = string(json, "action");
        ActionAffordance action = ActivityAffordanceCatalog.require(actionId, snapshot);
        BrainDirective directive = action.directive();
        ConversationResponse response = enumValue(ConversationResponse.class, string(json, "response"));
        if (!ConversationCatalog.optionsFor(snapshot, allowFreeform).contains(response))
            throw new IllegalArgumentException("model selected a response outside the offered menu");
        int target = action.targetEntityId();
        String skill = string(json, "skill");
        String fact = string(json, "fact");
        String say = string(json, "say");

        validateDirective(directive, snapshot);
        if (!skill.isBlank()) {
            SkillChoice choice = snapshot.skillChoices().stream().filter(value -> value.id().equals(skill))
                    .findFirst().orElseThrow(() -> new IllegalArgumentException("model selected an unknown skill"));
            if (!choice.ready() && response != ConversationResponse.SKILL_NOT_READY)
                throw new IllegalArgumentException("model selected a skill that is not ready");
            if (directive != BrainDirective.ADVISE && directive != choice.directive())
                throw new IllegalArgumentException("model selected a skill for an incompatible directive");
        }
        if (!fact.isBlank() && !snapshot.recalledFacts().containsKey(fact))
            throw new IllegalArgumentException("model selected an unknown fact");
        if (response == ConversationResponse.FREEFORM_GROUNDED && !allowFreeform)
            throw new IllegalArgumentException("free-form response is disabled");
        if (response != ConversationResponse.FREEFORM_GROUNDED) say = "";

        String taskKey = action.taskKey();
        String dialogue = ConversationCatalog.render(response, snapshot, skill, fact, say);
        if (dialogue.isBlank()) throw new IllegalArgumentException("model produced an empty response");
        return new BrainDecision(snapshot.requestId(), directive, target, taskKey, action.id(), skill,
                response.name(), dialogue);
    }

    private static void validateDirective(BrainDirective directive, BrainSnapshot snapshot) {
        boolean valid = switch (directive) {
            case ADVISE, IDLE, FOLLOW, WAIT -> true;
            case DEFEND, RETREAT -> !snapshot.threats().isEmpty();
            case EXECUTE_TASK, REQUEST_BLUEPRINT -> !snapshot.activeTask().isBlank();
        };
        if (!valid) throw new IllegalArgumentException("directive is not legal for this snapshot");
        if (!snapshot.question().isBlank() && directive != BrainDirective.ADVISE && directive != BrainDirective.IDLE)
            throw new IllegalArgumentException("questions may not change companion mode");
    }

    private static JsonObject objectFrom(String output) {
        if (output == null) throw new IllegalArgumentException("empty model output");
        int start = output.indexOf('{');
        int end = output.lastIndexOf('}');
        if (start < 0 || end < start) throw new IllegalArgumentException("model output is not JSON");
        return JsonParser.parseString(output.substring(start, end + 1)).getAsJsonObject();
    }

    private static String string(JsonObject object, String key) {
        return object.has(key) && !object.get(key).isJsonNull() ? object.get(key).getAsString().strip() : "";
    }

    private static <E extends Enum<E>> E enumValue(Class<E> type, String value) {
        try {
            return Enum.valueOf(type, value.toUpperCase(Locale.ROOT));
        } catch (RuntimeException error) {
            throw new IllegalArgumentException("unknown " + type.getSimpleName() + " value", error);
        }
    }
}

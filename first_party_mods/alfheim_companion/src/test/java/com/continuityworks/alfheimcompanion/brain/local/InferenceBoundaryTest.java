package com.continuityworks.alfheimcompanion.brain.local;

import com.continuityworks.alfheimcompanion.brain.BrainDecision;
import com.continuityworks.alfheimcompanion.brain.BrainDirective;
import com.continuityworks.alfheimcompanion.brain.BrainSnapshot;
import com.continuityworks.alfheimcompanion.brain.QuestContext;
import com.continuityworks.alfheimcompanion.brain.SkillChoice;
import net.minecraft.core.BlockPos;
import org.junit.jupiter.api.Test;

import java.net.URI;
import java.nio.file.Path;
import java.time.Duration;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;

class InferenceBoundaryTest {
    @Test
    void refusesNonLoopbackEndpoint() {
        assertThrows(IllegalArgumentException.class, () -> new InferenceSettings(true,
                URI.create("https://example.com/v1/chat/completions"), "model", Duration.ofSeconds(5),
                64, false, false, Path.of("java"), Path.of("worker"), Path.of("model"), 300));
    }

    @Test
    void configuredPathsCannotEscapeGameDirectory() {
        Properties properties = new Properties();
        properties.setProperty("worker_directory", "../outside");
        assertThrows(IllegalArgumentException.class,
                () -> InferenceSettings.from(properties, Path.of("game")));
    }

    @Test
    void promptIsBoundedAndContainsOnlyOfferedChoices() {
        String prompt = InferencePrompt.user(snapshot("Which skill fits this quest?"), false);
        assertTrue(prompt.length() <= 1200);
        assertTrue(prompt.contains("skill=mns:basic_attack"));
        assertTrue(prompt.contains("quest=q1"));
        assertTrue(prompt.contains("action_options=[ANSWER_ONLY:COMPANIONSHIP]"));
    }

    @Test
    void validTemplateSelectionIsAssembledByJava() {
        BrainDecision decision = InferenceResponseParser.parse("""
                {"directive":"RETREAT","target":42,"action":"ANSWER_ONLY","skill":"mns:basic_attack",
                 "response":"SKILL_RECOMMENDATION","fact":"","say":""}
                """, snapshot("Which skill should I use?"), false);
        assertEquals(BrainDirective.ADVISE, decision.directive());
        assertEquals(0, decision.targetEntityId());
        assertEquals("ANSWER_ONLY", decision.selectedActionId());
        assertEquals("mns:basic_attack", decision.selectedSkillId());
        assertEquals("I recommend Basic Attack for single target damage.", decision.dialogue());
    }

    @Test
    void actionMenuDerivesDirectiveAndTargetInsideJava() {
        BrainSnapshot activity = snapshot("");
        BrainDecision decision = InferenceResponseParser.parse("""
                {"action":"DEFEND_NEAREST","skill":"mns:basic_attack",
                 "response":"DEFEND_WARNING","fact":"","say":""}
                """, activity, false);
        assertEquals(BrainDirective.DEFEND, decision.directive());
        assertEquals(42, decision.targetEntityId());
        assertEquals("defend_owner", decision.taskKey());
    }

    @Test
    void rejectsInventedSkillAndQuestionSideEffects() {
        BrainSnapshot snapshot = snapshot("What should we do?");
        assertThrows(IllegalArgumentException.class, () -> InferenceResponseParser.parse("""
                {"action":"ANSWER_ONLY","skill":"mns:invented",
                 "response":"SKILL_RECOMMENDATION","fact":"","say":""}
                """, snapshot, false));
        assertThrows(IllegalArgumentException.class, () -> InferenceResponseParser.parse("""
                {"action":"RETREAT_TO_OWNER","skill":"",
                 "response":"RETREAT_WARNING","fact":"","say":""}
                """, snapshot, false));
    }

    @Test
    void freeformMustBeExplicitlyEnabled() {
        assertThrows(IllegalArgumentException.class, () -> InferenceResponseParser.parse("""
                {"action":"ANSWER_ONLY","skill":"",
                 "response":"FREEFORM_GROUNDED","fact":"","say":"A guess"}
                """, snapshot("Unknown question"), false));
    }

    private static BrainSnapshot snapshot(String question) {
        return new BrainSnapshot(7, 100, UUID.randomUUID(), UUID.randomUUID(), "Aelara",
                "minecraft:overworld", "minecraft:forest", "day", "clear", "following",
                BlockPos.ZERO, new BlockPos(2, 64, 2), 80, 90, 16, 75,
                List.of(new BrainSnapshot.Threat(42, "minecraft:zombie", 9)), "", "NONE", "balanced",
                question, "patient and concise", "Mine and Slash level 12",
                List.of(new QuestContext("q1", "Goblin Cave", "ACTIVE", "Defeat the raiders",
                        List.of("Raiders 3/5"), List.of())),
                List.of(new SkillChoice("mns:basic_attack", "Basic Attack", "single target damage",
                        BrainDirective.DEFEND,
                        true, "none", 0, "target in melee range")),
                Map.of("home_court", "hollow_court"));
    }
}

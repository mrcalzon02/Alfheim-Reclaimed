package com.continuityworks.alfheimcompanion.brain;

import net.minecraft.core.BlockPos;

import java.util.List;
import java.util.Map;
import java.util.UUID;

public record BrainSnapshot(
        long requestId,
        long gameTime,
        UUID companionUuid,
        UUID ownerUuid,
        String companionName,
        String dimensionId,
        String biome,
        String timeOfDay,
        String weather,
        String mode,
        BlockPos companionPosition,
        BlockPos ownerPosition,
        int ownerHealthPercent,
        int companionHealthPercent,
        int nutrition,
        int stamina,
        List<Threat> threats,
        String activeTask,
        String basePhase,
        String behaviorPreset,
        String question,
        String personality,
        String combatProfile,
        List<QuestContext> quests,
        List<SkillChoice> skillChoices,
        Map<String, String> recalledFacts
) {
    public BrainSnapshot {
        threats = List.copyOf(threats).subList(0, Math.min(3, threats.size()));
        question = question == null ? "" : question.strip();
        basePhase = basePhase == null ? "NONE" : basePhase.strip();
        behaviorPreset = behaviorPreset == null ? "balanced" : behaviorPreset.strip();
        companionName = companionName == null ? "Companion" : companionName.strip();
        quests = List.copyOf(quests).subList(0, Math.min(3, quests.size()));
        skillChoices = List.copyOf(skillChoices).subList(0, Math.min(8, skillChoices.size()));
        recalledFacts = Map.copyOf(recalledFacts);
    }

    public record Threat(int entityId, String entityType, int distanceSquared) {}
}

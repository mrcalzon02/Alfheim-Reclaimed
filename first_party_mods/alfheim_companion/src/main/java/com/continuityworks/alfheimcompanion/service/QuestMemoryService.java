package com.continuityworks.alfheimcompanion.service;

import com.continuityworks.alfheimcompanion.api.quest.QuestProvider;
import com.continuityworks.alfheimcompanion.integration.QuestAwarenessBridge;
import com.continuityworks.alfheimcompanion.memory.CompanionSavedData;
import com.continuityworks.alfheimcompanion.memory.MemoryEntry;
import net.minecraft.server.level.ServerPlayer;

public final class QuestMemoryService {
    private QuestMemoryService() {}

    public static void refresh(ServerPlayer owner, CompanionSavedData data) {
        QuestAwarenessBridge.provider().ifPresent(provider -> {
            for (QuestProvider.QuestView quest : provider.questsFor(owner)) {
                if (quest.status() == QuestProvider.Status.NOT_AVAILABLE) continue;
                String key = "quest:" + quest.id();
                String next = quest.status().name();
                String previous = data.facts().get(key);
                if (!next.equals(previous)) {
                    data.rememberFact(key, next);
                    data.remember(new MemoryEntry(owner.level().getGameTime(), "quest", quest.name(),
                            previous == null ? "Discovered: " + quest.goal() : previous + " -> " + next, 7));
                }
            }
        });
    }
}

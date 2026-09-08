package com.continuityworks.alfheimcompanion.api.quest;

import net.minecraft.server.level.ServerPlayer;

import java.util.List;

/** Optional adapter endpoint implemented against the installed FTB Quests version. */
public interface QuestProvider {
    int API_VERSION = 1;

    int apiVersion();

    List<QuestView> questsFor(ServerPlayer player);

    enum Status { NOT_AVAILABLE, AVAILABLE, ACTIVE, COMPLETED }

    record QuestView(String id, String name, String goal, Status status,
                     List<ObjectiveView> objectives, List<IngredientView> ingredients,
                     List<String> criteria) {
        public QuestView {
            objectives = List.copyOf(objectives);
            ingredients = List.copyOf(ingredients);
            criteria = List.copyOf(criteria);
        }
    }

    record ObjectiveView(String id, String description, int current, int required, boolean complete) {}
    record IngredientView(String itemOrTagId, int required, int available) {}
}

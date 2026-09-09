package com.continuityworks.alfheimcompanion.brain;

import java.util.List;

/** Immutable, bounded quest evidence supplied to a reasoning engine. */
public record QuestContext(
        String id,
        String name,
        String status,
        String goal,
        List<String> objectives,
        List<String> missingIngredients
) {
    public QuestContext {
        id = limit(id, 64);
        name = limit(name, 96);
        status = limit(status, 24);
        goal = limit(goal, 180);
        objectives = bounded(objectives, 4, 120);
        missingIngredients = bounded(missingIngredients, 4, 96);
    }

    private static List<String> bounded(List<String> values, int count, int length) {
        if (values == null) return List.of();
        return values.stream().limit(count).map(value -> limit(value, length)).toList();
    }

    private static String limit(String value, int maximum) {
        if (value == null) return "";
        String clean = value.replace('\n', ' ').replace('\r', ' ').strip();
        return clean.length() <= maximum ? clean : clean.substring(0, maximum);
    }
}

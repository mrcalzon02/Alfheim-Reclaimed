package com.continuityworks.alfheimcompanion.brain;

/** A deterministic adapter-provided action that the model may select but may not execute itself. */
public record SkillChoice(
        String id,
        String name,
        String role,
        BrainDirective directive,
        boolean ready,
        String resource,
        int cost,
        String constraint
) {
    public SkillChoice {
        id = limit(id, 64);
        name = limit(name, 64);
        role = limit(role, 64);
        if (directive == null) throw new IllegalArgumentException("skill directive");
        resource = limit(resource, 32);
        cost = Math.max(0, cost);
        constraint = limit(constraint, 96);
        if (id.isBlank()) throw new IllegalArgumentException("skill id");
    }

    private static String limit(String value, int maximum) {
        if (value == null) return "";
        String clean = value.replace('\n', ' ').replace('\r', ' ').strip();
        return clean.length() <= maximum ? clean : clean.substring(0, maximum);
    }
}

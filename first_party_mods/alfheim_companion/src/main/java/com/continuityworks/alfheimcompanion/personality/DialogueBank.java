package com.continuityworks.alfheimcompanion.personality;

import java.util.List;

public final class DialogueBank {
    public enum Moment { SUMMON, SUMMON_CRANKY, DISMISS, FOLLOW, WAIT, DEFEND, RETREAT, WORK_COMPLETE }

    private static final List<String> ADJECTIVES = List.of(
            "bright", "patient", "ancient", "verdant", "silver", "quiet", "steadfast", "starlit"
    );
    private static final List<String> SUMMON = List.of(
            "The %s paths open. I am here.", "You called through the %s veil; I have answered.",
            "The %s road from Alfheim remembers us."
    );
    private static final List<String> DISMISS = List.of(
            "I return by the %s path until you call again.", "The %s veil closes, but our bond remains.",
            "Until the sigil opens the %s road again."
    );
    private static final List<String> SUMMON_CRANKY = List.of(
            "Again? The veil has scarcely settled.", "Must we keep folding space like a handkerchief?",
            "I heard you the first time. The %s path is not a revolving door."
    );
    private static final List<String> FOLLOW = List.of(
            "I will follow.", "Lead on; I am beside you.", "Our path is one."
    );
    private static final List<String> WAIT = List.of(
            "I will keep watch here.", "I shall hold this ground.", "Return when you are ready."
    );
    private static final List<String> DEFEND = List.of(
            "Stay close. I see danger.", "I will guard you.", "They will not pass me."
    );
    private static final List<String> RETREAT = List.of(
            "Fall back. I will cover us.", "We must yield this ground for now.", "To safety—quickly."
    );
    private static final List<String> WORK_COMPLETE = List.of(
            "The work is complete.", "The final piece rests true.", "Our design now stands."
    );

    private DialogueBank() {}

    public static String line(Moment moment, long seed) {
        List<String> lines = switch (moment) {
            case SUMMON -> SUMMON;
            case SUMMON_CRANKY -> SUMMON_CRANKY;
            case DISMISS -> DISMISS;
            case FOLLOW -> FOLLOW;
            case WAIT -> WAIT;
            case DEFEND -> DEFEND;
            case RETREAT -> RETREAT;
            case WORK_COMPLETE -> WORK_COMPLETE;
        };
        String line = lines.get(Math.floorMod(Long.hashCode(seed), lines.size()));
        if (line.contains("%s")) {
            String adjective = ADJECTIVES.get(Math.floorMod(Long.hashCode(seed * 31L), ADJECTIVES.size()));
            return line.formatted(adjective);
        }
        return line;
    }
}

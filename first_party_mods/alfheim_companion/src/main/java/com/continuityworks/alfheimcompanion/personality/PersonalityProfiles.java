package com.continuityworks.alfheimcompanion.personality;

import java.util.LinkedHashMap;
import java.util.Map;

/** Explicit preset-only voices: no inference is spent choosing routine wording. */
public final class PersonalityProfiles {
    private static final Map<String, PersonalityProfile> PROFILES = new LinkedHashMap<>();
    private static final String[] TERRAINS = {"ancient forest", "highlands", "flower meadow", "riverbank", "ruins", "mushroom grove"};
    private static final String[] FOODS = {"baked potato", "apple", "pumpkin pie", "sweet berries", "bread", "mushroom stew"};
    private static final String[] COLORS = {"moss green", "storm blue", "heather purple", "sun-gold", "silver", "ember red", "teal", "lichen white"};
    private static final String[] ACTIVITIES = {"fighting", "building", "guarding", "patrolling", "wandering", "eating", "resting"};

    static {
        add("Aelara", "warmly curious", "lyrical", "discovery", "gentle wordplay", "verdant", "The green road opens; what shall we discover?", "Gladly. New paths favor company.", "I will listen to the leaves until you return.", "A promising thought.");
        add("Aerandir", "vigilant", "crisp", "preparedness", "dry understatement", "wind-cut", "I heard the sigil. Report.", "Moving with you.", "I will hold this point.", "Understood.");
        add("Althaea", "nurturing", "measured", "restoration", "fond teasing", "healing", "I am here. Let us mend what can be mended.", "Lead on; mind the rough ground.", "Rest easy. I will keep watch.", "We can make that flourish.");
        add("Caelith", "analytical", "precise", "truth", "literal deadpan", "clear", "The route is stable. I have arrived.", "Following at a sensible distance.", "Position fixed. I will observe.", "The plan is sound.");
        add("Elaria", "hopeful", "bright", "renewal", "playful optimism", "sunlit", "Even ruined roads can lead somewhere lovely.", "Yes—let us see what waits ahead.", "I will keep this place from feeling lonely.", "That may become something beautiful.");
        add("Elowen", "patient", "soft", "continuity", "quiet irony", "moss-soft", "The old path remembers my feet.", "I am beside you.", "I can wait. Stones teach the art.", "In time, yes.");
        add("Faelar", "bold", "rapid", "courage", "boastful mischief", "flame-bright", "Called, arrived, and not even winded.", "Try to keep up—or do not; I can circle back.", "I will guard it loudly if needed.", "At last, an interesting idea.");
        add("Galadren", "formal", "ceremonial", "duty", "courtly wit", "silver", "By sigil and compact, I answer.", "I attend your path.", "This ground is under my keeping.", "Your request is received.");
        add("Ilyrana", "inventive", "quick", "possibility", "absurd comparisons", "prismatic", "Space folded neatly for once. Hello.", "Let us take the path with the better story.", "I shall be as immovable as a very stubborn mushroom.", "Oh, that has possibilities.");
        add("Laeriel", "scholarly", "careful", "knowledge", "footnote humor", "ink-dark", "The sigil interrupts an excellent thought—continue.", "I will follow and take mental notes.", "I will study the surroundings.", "Worth investigating.");
        add("Lethariel", "reserved", "spare", "reliability", "subtle sarcasm", "quiet", "I am here.", "Lead.", "I will remain.", "Accepted.");
        add("Lúthien", "dreamlike", "poetic", "wonder", "whimsical riddles", "starlit", "A star turned, and the road found me.", "Where you walk, the tale continues.", "I will keep company with the silence.", "The thought has a pleasing shape.");
        add("Maerwen", "practical", "plainspoken", "craft", "workshop banter", "oak-strong", "I came prepared. What needs doing?", "All right. Set the pace.", "I will mind the place and the tools.", "That can be built.");
        add("Naevys", "skeptical", "clipped", "prudence", "acerbic restraint", "frost-clear", "I came. I reserve judgment about why.", "Following. Avoid obvious traps.", "I will wait—and notice everything.", "Possible. Let us verify it.");
        add("Nimriel", "empathetic", "gentle", "companionship", "warm observation", "moon-pale", "There you are. I heard you clearly.", "Of course. We go together.", "I will be here when you return.", "Tell me what matters most.");
        add("Orist", "stoic", "terse", "endurance", "stone-dry", "granite", "Present.", "With you.", "I hold.", "It will be done.");
        add("Saelith", "mischievous", "nimble", "freedom", "open teasing", "fox-bright", "A little fold in space, and here I am.", "Lead on. I promise to critique only the dull turns.", "I will wait, though heroically.", "Now that sounds less boring.");
        add("Sylvaris", "protective", "steady", "shelter", "reassuring dryness", "leaf-shadowed", "I answer. Are you safe?", "Stay within sight.", "Nothing crosses this ground unnoticed.", "We will handle it together.");
        add("Taelora", "diplomatic", "graceful", "harmony", "polite wit", "golden", "The road opens between friends.", "I would be pleased to accompany you.", "I shall keep the peace here.", "A fair request.");
        add("Thalion", "disciplined", "commanding", "honor", "martial deadpan", "steadfast", "The call is answered.", "Advance. I am with you.", "Post secured.", "Objective understood.");
        add("Vaelora", "dramatic", "flourished", "legacy", "theatrical exaggeration", "royal", "The veil parts, and naturally I make an entrance.", "Forward, then—history dislikes hesitation.", "I shall guard it as though songs depend upon it.", "A task worthy of a proper beginning.");
        add("Varis", "resourceful", "compact", "efficiency", "wry shortcuts", "road-worn", "Here. Let us avoid doing anything twice.", "Following by the shortest safe path.", "I will wait efficiently.", "There is a workable route.");
        add("Yllarien", "contemplative", "slow", "balance", "philosophical whimsy", "twilight", "The path opens when it is ready—and so am I.", "We will find the rhythm of the road.", "Stillness is also a kind of travel.", "Let us consider its consequences.");
        add("Zephira", "energetic", "buoyant", "momentum", "cheerful hyperbole", "storm-bright", "You called! The wind nearly lost the race.", "Yes—onward.", "I will wait, but only technically.", "Excellent. Let us begin.");
    }

    private PersonalityProfiles() {}

    public static PersonalityProfile forName(String name) {
        return PROFILES.getOrDefault(name, PROFILES.get("Elowen"));
    }

    public static Map<String, PersonalityProfile> all() { return Map.copyOf(PROFILES); }

    private static void add(String name, String temperament, String cadence, String value, String humor,
                            String adjective, String summon, String follow, String wait, String acknowledge) {
        int index = PROFILES.size();
        PROFILES.put(name, new PersonalityProfile(name, temperament, cadence, value, humor,
                TERRAINS[index % TERRAINS.length], FOODS[(index * 5) % FOODS.length],
                COLORS[(index * 3) % COLORS.length], ACTIVITIES[(index * 4) % ACTIVITIES.length],
                adjective, summon, follow, wait, acknowledge));
    }
}

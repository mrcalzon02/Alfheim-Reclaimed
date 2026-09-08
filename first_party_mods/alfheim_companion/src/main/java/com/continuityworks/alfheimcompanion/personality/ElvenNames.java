package com.continuityworks.alfheimcompanion.personality;

import java.util.List;
import java.util.UUID;

public final class ElvenNames {
    private static final List<String> NAMES = List.of(
            "Aelara", "Aerandir", "Althaea", "Caelith", "Elaria", "Elowen",
            "Faelar", "Galadren", "Ilyrana", "Laeriel", "Lethariel", "Lúthien",
            "Maerwen", "Naevys", "Nimriel", "Orist", "Saelith", "Sylvaris",
            "Taelora", "Thalion", "Vaelora", "Varis", "Yllarien", "Zephira"
    );

    private ElvenNames() {}

    public static String select(UUID identity) {
        return NAMES.get(Math.floorMod(identity.hashCode(), NAMES.size()));
    }
}

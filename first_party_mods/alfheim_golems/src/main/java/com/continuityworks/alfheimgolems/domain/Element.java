package com.continuityworks.alfheimgolems.domain;

import java.util.Locale;
import java.util.Optional;

public enum Element {
    FIRE,
    WATER,
    EARTH,
    AIR;

    public String serializedName() {
        return name().toLowerCase(Locale.ROOT);
    }

    public static Optional<Element> fromSerializedName(String value) {
        if (value == null) return Optional.empty();
        for (Element element : values()) {
            if (element.serializedName().equals(value)) return Optional.of(element);
        }
        return Optional.empty();
    }
}

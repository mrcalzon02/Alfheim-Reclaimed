package com.continuityworks.alfheimgolems.domain;

import com.continuityworks.alfheimgolems.domain.Element;
import org.junit.jupiter.api.Test;

import java.util.Arrays;
import java.util.Set;
import java.util.stream.Collectors;

import static org.junit.jupiter.api.Assertions.*;

class ElementTest {
    @Test
    void hasExactlyFourStableSerializedValues() {
        assertEquals(Set.of("fire", "water", "earth", "air"),
                Arrays.stream(Element.values()).map(Element::serializedName).collect(Collectors.toSet()));
        for (Element element : Element.values()) {
            assertEquals(element, Element.fromSerializedName(element.serializedName()).orElseThrow());
        }
    }

    @Test
    void rejectsUnknownOrWrongCaseValues() {
        assertTrue(Element.fromSerializedName("shadow").isEmpty());
        assertTrue(Element.fromSerializedName("FIRE").isEmpty());
        assertTrue(Element.fromSerializedName(null).isEmpty());
    }
}

package com.continuityworks.alfheimcompanion.command;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class AddressedCommandParserTest {
    @Test
    void ignoresUnaddressedAndPartialNameMessages() {
        assertTrue(AddressedCommandParser.parse("Aelara", "follow me").isEmpty());
        assertTrue(AddressedCommandParser.parse("Aelara", "Aelarax follow").isEmpty());
        assertTrue(AddressedCommandParser.parse("Aelara", "Aelara").isEmpty());
    }

    @Test
    void parsesAddressAndClampsCount() {
        var parsed = AddressedCommandParser.parse("Aelara", "AELARA, fetch 900 spruce logs").orElseThrow();
        assertEquals(AddressedCommandParser.Verb.FETCH_ITEM, parsed.verb());
        assertEquals("spruce logs", parsed.target());
        assertEquals(64, parsed.count());
    }

    @Test
    void prioritizesLeadOverFetchPhrase() {
        var parsed = AddressedCommandParser.parse("Aelara", "Aelara: bring me to iron").orElseThrow();
        assertEquals(AddressedCommandParser.Verb.LEAD_TO_ITEM, parsed.verb());
        assertEquals("iron", parsed.target());
    }

    @Test
    void blueprintApprovalMustAlsoBeAddressed() {
        assertTrue(AddressedCommandParser.parse("Aelara", "approve blueprint").isEmpty());
        assertEquals(AddressedCommandParser.Verb.APPROVE_BLUEPRINT,
                AddressedCommandParser.parse("Aelara", "Aelara; approve blueprint").orElseThrow().verb());
    }
}

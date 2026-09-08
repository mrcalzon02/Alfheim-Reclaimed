package com.continuityworks.alfheimcompanion.personality;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class PersonalityProfilesTest {
    @Test
    void everySelectableNameHasOneDistinctCompleteProfile() {
        assertEquals(ElvenNames.all().size(), PersonalityProfiles.all().size());
        for (String name : ElvenNames.all()) {
            PersonalityProfile profile = PersonalityProfiles.forName(name);
            assertEquals(name, profile.name());
            assertFalse(profile.temperament().isBlank());
            assertFalse(profile.cadence().isBlank());
            assertFalse(profile.coreValue().isBlank());
            assertFalse(profile.humor().isBlank());
            assertFalse(profile.summonLine().isBlank());
            assertFalse(profile.followLine().isBlank());
            assertFalse(profile.waitLine().isBlank());
        }
        assertEquals(ElvenNames.all().size(), PersonalityProfiles.all().values().stream()
                .map(PersonalityProfile::promptSummary).distinct().count());
    }
}

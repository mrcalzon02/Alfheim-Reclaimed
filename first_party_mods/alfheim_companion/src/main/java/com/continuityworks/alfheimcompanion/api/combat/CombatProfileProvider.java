package com.continuityworks.alfheimcompanion.api.combat;

import java.util.List;
import java.util.Map;
import java.util.UUID;

/** Optional versioned MMO bridge; implementations normalize their system without granting items. */
public interface CombatProfileProvider {
    int API_VERSION = 1;
    int apiVersion();
    CombatProfile profile(UUID lesseeUuid, UUID companionUuid, List<String> equippedItemIds,
                          Map<String, Double> vanillaAttributes);
    boolean mayEquip(CombatProfile profile, String itemId);

    record CombatProfile(String systemId, int level, String archetype,
                         Map<String, Integer> resources, Map<String, Double> modifiers) {
        public CombatProfile {
            resources = Map.copyOf(resources);
            modifiers = Map.copyOf(modifiers);
        }
    }
}

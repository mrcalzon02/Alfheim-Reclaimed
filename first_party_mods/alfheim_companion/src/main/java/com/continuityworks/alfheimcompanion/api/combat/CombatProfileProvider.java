package com.continuityworks.alfheimcompanion.api.combat;

import java.util.Map;
import java.util.List;
import java.util.Optional;

import com.continuityworks.alfheimcompanion.brain.SkillChoice;

import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;

/** Optional versioned MMO bridge; implementations normalize their system without granting items. */
public interface CombatProfileProvider {
    int API_VERSION = 2;
    int apiVersion();
    CombatProfile profile(ServerPlayer lessee, LivingEntity companion);
    boolean recognizes(ItemStack stack);
    Optional<EquipmentSlot> equipmentSlot(ItemStack stack);
    boolean mayEquip(LivingEntity companion, ItemStack stack);

    /** Synchronizes level/state without granting experience, items, or permissions. */
    void synchronize(ServerPlayer lessee, LivingEntity companion);

    /** Invalidates the MMO system's calculated gear cache after a legitimate slot mutation. */
    void onEquipmentChanged(LivingEntity companion);

    /**
     * Returns only skills that deterministic game code can validate for this companion. An empty
     * list is safer than describing player-only or otherwise non-executable skills.
     */
    default List<SkillChoice> availableSkills(ServerPlayer lessee, LivingEntity companion) {
        return List.of();
    }

    record CombatProfile(String systemId, int level, String archetype,
                         Map<String, Integer> resources, Map<String, Double> modifiers) {
        public CombatProfile {
            resources = Map.copyOf(resources);
            modifiers = Map.copyOf(modifiers);
        }
    }
}

package com.continuityworks.alfheimcompanion.service;

import com.continuityworks.alfheimcompanion.entity.ElvenCompanionEntity;
import com.continuityworks.alfheimcompanion.integration.GraveIntegrationBridge;
import com.continuityworks.alfheimcompanion.memory.CompanionSavedData;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.GameRules;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.LinkedHashMap;
import java.util.UUID;

public final class CompanionDeathInventoryService {
    private static final EquipmentSlot[] EQUIPMENT = {EquipmentSlot.HEAD, EquipmentSlot.CHEST,
            EquipmentSlot.LEGS, EquipmentSlot.FEET, EquipmentSlot.MAINHAND, EquipmentSlot.OFFHAND};

    private CompanionDeathInventoryService() {}

    /**
     * Normal dismissal must never delete the companion's 36-slot cargo or equipment.
     * Save copies before clearing the entity, then let the summon path restore them only
     * after the new entity has been accepted by Forge. This is not a death or a grave.
     *
     * @return false when the caller cannot prove ownership; no inventory was changed.
     */
    public static boolean retainForDismiss(ElvenCompanionEntity companion,
                                           CompanionSavedData data, UUID expectedOwner) {
        if (expectedOwner == null || !expectedOwner.equals(companion.ownerUuid())) return false;

        List<ItemStack> carried = new ArrayList<>();
        Map<String, ItemStack> equipment = new LinkedHashMap<>();
        for (int index = 0; index < companion.inventory().getContainerSize(); index++) {
            ItemStack stack = companion.inventory().getItem(index);
            if (!stack.isEmpty()) carried.add(stack.copy());
        }
        for (EquipmentSlot slot : EQUIPMENT) {
            ItemStack stack = companion.getItemBySlot(slot);
            if (!stack.isEmpty()) equipment.put(slot.getName(), stack.copy());
        }

        // If persistence rejects the snapshot, do not clear or discard any player items.
        data.storeFallenInventory(expectedOwner, carried, equipment);
        companion.inventory().clearContent();
        for (EquipmentSlot slot : EQUIPMENT) companion.setItemSlot(slot, ItemStack.EMPTY);
        return true;
    }

    public static void handle(ElvenCompanionEntity companion, CompanionSavedData data) {
        List<ItemStack> contents = new ArrayList<>();
        List<ItemStack> carried = new ArrayList<>();
        Map<String, ItemStack> equipment = new LinkedHashMap<>();
        for (int slot = 0; slot < companion.inventory().getContainerSize(); slot++) {
            ItemStack stack = companion.inventory().getItem(slot);
            if (!stack.isEmpty()) {
                contents.add(stack.copy());
                carried.add(stack.copy());
            }
        }
        for (EquipmentSlot slot : EQUIPMENT) {
            ItemStack stack = companion.getItemBySlot(slot);
            if (!stack.isEmpty()) {
                contents.add(stack.copy());
                equipment.put(slot.getName(), stack.copy());
            }
        }
        ServerPlayer lessee = companion.resolveOwner();
        boolean keep = companion.level().getGameRules().getBoolean(GameRules.RULE_KEEPINVENTORY);
        boolean graveCaptured = lessee != null && !keep
                && GraveIntegrationBridge.capture(lessee, companion, contents);

        if (keep && companion.ownerUuid() != null)
            data.storeFallenInventory(companion.ownerUuid(), carried, equipment);
        else if (!graveCaptured) contents.forEach(companion::spawnAtLocation);

        companion.inventory().clearContent();
        for (EquipmentSlot slot : EQUIPMENT) companion.setItemSlot(slot, ItemStack.EMPTY);
    }
}

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

public final class CompanionDeathInventoryService {
    private static final EquipmentSlot[] EQUIPMENT = {EquipmentSlot.HEAD, EquipmentSlot.CHEST,
            EquipmentSlot.LEGS, EquipmentSlot.FEET, EquipmentSlot.MAINHAND, EquipmentSlot.OFFHAND};

    private CompanionDeathInventoryService() {}

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

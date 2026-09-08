package com.continuityworks.alfheimcompanion.service;

import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.AxeItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.ShieldItem;
import net.minecraft.world.item.SwordItem;

import java.util.Optional;

/** Deliberately small auto-use allowlist; unfamiliar modded gear is carried, never guessed at. */
public final class EquipmentPolicy {
    private EquipmentPolicy() {}

    public static Optional<EquipmentSlot> understoodSlot(ItemStack stack) {
        if (stack.getItem() instanceof ArmorItem armor) return Optional.of(armor.getEquipmentSlot());
        if (stack.getItem() instanceof ShieldItem) return Optional.of(EquipmentSlot.OFFHAND);
        if (stack.getItem() instanceof SwordItem || stack.getItem() instanceof AxeItem)
            return Optional.of(EquipmentSlot.MAINHAND);
        return Optional.empty();
    }
}

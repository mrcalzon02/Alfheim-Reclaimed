package com.continuityworks.alfheimcompanion.service;

import com.continuityworks.alfheimcompanion.integration.CombatProfileBridge;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
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

    public static Decision evaluate(LivingEntity companion, ItemStack stack) {
        boolean mmoGear = CombatProfileBridge.recognizes(stack);
        Optional<EquipmentSlot> slot = mmoGear
                ? CombatProfileBridge.equipmentSlot(stack) : understoodSlot(stack);
        boolean eligible = !mmoGear || CombatProfileBridge.mayEquip(companion, stack);
        return new Decision(slot, mmoGear || slot.isPresent(), eligible, mmoGear);
    }

    public record Decision(Optional<EquipmentSlot> slot, boolean understood,
                           boolean eligible, boolean mmoGear) {}
}

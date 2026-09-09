package com.continuityworks.alfheimcompanion.integration;

import com.continuityworks.alfheimcompanion.api.combat.CombatProfileProvider;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;

import java.util.Objects;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicReference;
import com.continuityworks.alfheimcompanion.brain.SkillChoice;

public final class CombatProfileBridge {
    private static final AtomicReference<CombatProfileProvider> PROVIDER = new AtomicReference<>();
    private CombatProfileBridge() {}

    public static void register(CombatProfileProvider provider) {
        Objects.requireNonNull(provider);
        if (provider.apiVersion() != CombatProfileProvider.API_VERSION)
            throw new IllegalArgumentException("Unsupported combat profile API version " + provider.apiVersion());
        if (!PROVIDER.compareAndSet(null, provider))
            throw new IllegalStateException("A combat profile provider is already registered");
    }

    public static Optional<CombatProfileProvider> provider() { return Optional.ofNullable(PROVIDER.get()); }

    public static boolean recognizes(ItemStack stack) {
        CombatProfileProvider provider = PROVIDER.get();
        if (provider == null) return false;
        try { return provider.recognizes(stack); }
        catch (RuntimeException | LinkageError ignored) { return false; }
    }

    public static Optional<EquipmentSlot> equipmentSlot(ItemStack stack) {
        CombatProfileProvider provider = PROVIDER.get();
        if (provider == null) return Optional.empty();
        try { return provider.equipmentSlot(stack); }
        catch (RuntimeException | LinkageError ignored) { return Optional.empty(); }
    }

    public static boolean mayEquip(LivingEntity companion, ItemStack stack) {
        CombatProfileProvider provider = PROVIDER.get();
        if (provider == null) return true;
        try { return provider.mayEquip(companion, stack); }
        catch (RuntimeException | LinkageError ignored) { return false; }
    }

    public static void synchronize(ServerPlayer lessee, LivingEntity companion) {
        CombatProfileProvider provider = PROVIDER.get();
        if (provider != null) provider.synchronize(lessee, companion);
    }

    public static void onEquipmentChanged(LivingEntity companion) {
        CombatProfileProvider provider = PROVIDER.get();
        if (provider == null) return;
        try { provider.onEquipmentChanged(companion); }
        catch (RuntimeException | LinkageError ignored) { }
    }

    public static String statusSuffix(ServerPlayer lessee, LivingEntity companion) {
        CombatProfileProvider provider = PROVIDER.get();
        if (provider == null) return "";
        try {
            CombatProfileProvider.CombatProfile profile = provider.profile(lessee, companion);
            return " " + profile.systemId() + " level " + profile.level() + ", " + profile.archetype() + ".";
        } catch (RuntimeException | LinkageError ignored) {
            return " MMO profile unavailable.";
        }
    }

    public static List<SkillChoice> availableSkills(ServerPlayer lessee, LivingEntity companion) {
        CombatProfileProvider provider = PROVIDER.get();
        if (provider == null) return List.of();
        try {
            return provider.availableSkills(lessee, companion).stream()
                    .filter(Objects::nonNull).limit(8).toList();
        } catch (RuntimeException | LinkageError ignored) {
            return List.of();
        }
    }
}

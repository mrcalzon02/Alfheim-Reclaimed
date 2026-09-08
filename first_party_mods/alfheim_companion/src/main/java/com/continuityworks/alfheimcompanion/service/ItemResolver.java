package com.continuityworks.alfheimcompanion.service;

import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.Item;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.Comparator;
import java.util.Locale;
import java.util.Optional;

public final class ItemResolver {
    private ItemResolver() {}

    public static Optional<Item> resolve(String query) {
        String normalized = query.toLowerCase(Locale.ROOT).strip().replace(' ', '_');
        ResourceLocation direct = ResourceLocation.tryParse(normalized);
        if (direct != null && ForgeRegistries.ITEMS.containsKey(direct)) {
            return Optional.ofNullable(ForgeRegistries.ITEMS.getValue(direct));
        }
        return ForgeRegistries.ITEMS.getKeys().stream()
                .filter(id -> id.getPath().equals(normalized) || id.getPath().endsWith("_" + normalized)
                        || id.toString().contains(normalized))
                .min(Comparator.comparingInt(id -> id.toString().length()))
                .map(ForgeRegistries.ITEMS::getValue);
    }
}

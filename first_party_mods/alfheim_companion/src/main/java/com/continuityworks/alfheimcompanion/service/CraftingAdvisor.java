package com.continuityworks.alfheimcompanion.service;

import com.continuityworks.alfheimcompanion.entity.ElvenCompanionEntity;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.CraftingRecipe;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.item.crafting.RecipeType;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

public final class CraftingAdvisor {
    private CraftingAdvisor() {}

    public static String describe(ServerPlayer owner, ElvenCompanionEntity companion, String query, int desired) {
        Optional<Item> target = ItemResolver.resolve(query);
        if (target.isEmpty()) return "I do not recognize an item called " + query + ".";
        List<CraftingRecipe> matches = owner.server.getRecipeManager().getAllRecipesFor(RecipeType.CRAFTING).stream()
                .filter(recipe -> recipe.getResultItem(owner.server.registryAccess()).is(target.get()))
                .toList();
        if (matches.isEmpty()) return "I found no ordinary crafting recipe for " + target.get().getDescription().getString() + ".";

        CraftingRecipe recipe = matches.get(0);
        int crafts = Math.max(1, (int) Math.ceil(desired /
                (double) Math.max(1, recipe.getResultItem(owner.server.registryAccess()).getCount())));
        List<String> needs = new ArrayList<>();
        for (Ingredient ingredient : recipe.getIngredients()) {
            if (ingredient.isEmpty()) continue;
            ItemStack[] choices = ingredient.getItems();
            if (choices.length == 0) continue;
            String name = choices[0].getHoverName().getString();
            boolean has = count(owner, companion, choices[0].getItem()) >= crafts;
            needs.add(crafts + "× " + name + (has ? " ✓" : " (needed)"));
        }
        return "For " + desired + "× " + target.get().getDescription().getString() + ", use "
                + String.join(", ", needs) + ".";
    }

    private static int count(ServerPlayer owner, ElvenCompanionEntity companion, Item item) {
        int count = 0;
        for (ItemStack stack : owner.getInventory().items) if (stack.is(item)) count += stack.getCount();
        for (int i = 0; i < companion.inventory().getContainerSize(); i++) {
            ItemStack stack = companion.inventory().getItem(i);
            if (stack.is(item)) count += stack.getCount();
        }
        return count;
    }
}

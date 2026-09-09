package com.continuityworks.alfheimgolems.order;

import net.minecraft.world.item.ItemStack;

/** A bounded, server-owned item predicate. Implementations must be serializable by a known type ID. */
public interface ItemFilter {
    boolean matches(ItemStack stack);

    String typeId();

    static ItemFilter any() {
        return AnyItemFilter.INSTANCE;
    }

    final class AnyItemFilter implements ItemFilter {
        private static final AnyItemFilter INSTANCE = new AnyItemFilter();

        private AnyItemFilter() {}

        @Override
        public boolean matches(ItemStack stack) {
            return stack != null && !stack.isEmpty();
        }

        @Override
        public String typeId() {
            return "any";
        }
    }
}

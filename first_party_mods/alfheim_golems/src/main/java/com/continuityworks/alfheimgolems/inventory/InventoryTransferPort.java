package com.continuityworks.alfheimgolems.inventory;

import net.minecraft.world.item.ItemStack;

/**
 * Mutation boundary used by the scheduler. Every implementation must simulate before commit and
 * return actual remainders rather than assuming another handler accepted a stack.
 */
public interface InventoryTransferPort {
    TransferSimulation simulate(TransferRequest request);

    ItemStack extractToGolem(TransferRequest request, int count);

    ItemStack insertFromGolem(TransferRequest request, ItemStack carried);
}

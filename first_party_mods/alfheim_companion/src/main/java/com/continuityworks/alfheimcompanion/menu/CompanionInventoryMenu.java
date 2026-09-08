package com.continuityworks.alfheimcompanion.menu;

import com.continuityworks.alfheimcompanion.entity.ElvenCompanionEntity;
import com.continuityworks.alfheimcompanion.registry.ModMenus;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.world.Container;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.ItemStack;

public final class CompanionInventoryMenu extends AbstractContainerMenu {
    public static final int COMPANION_SLOTS = 36;
    private final ElvenCompanionEntity companion;
    private final Container container;

    public CompanionInventoryMenu(int containerId, Inventory playerInventory, ElvenCompanionEntity companion) {
        super(ModMenus.COMPANION_INVENTORY.get(), containerId);
        this.companion = companion;
        this.container = companion == null ? new SimpleContainer(COMPANION_SLOTS) : companion.inventory();
        checkContainerSize(container, COMPANION_SLOTS);
        container.startOpen(playerInventory.player);

        for (int row = 0; row < 4; row++) {
            for (int column = 0; column < 9; column++) {
                addSlot(new Slot(container, column + row * 9, 8 + column * 18, 18 + row * 18));
            }
        }
        for (int row = 0; row < 3; row++) {
            for (int column = 0; column < 9; column++) {
                addSlot(new Slot(playerInventory, column + row * 9 + 9, 8 + column * 18, 103 + row * 18));
            }
        }
        for (int column = 0; column < 9; column++) {
            addSlot(new Slot(playerInventory, column, 8 + column * 18, 161));
        }
    }

    public static CompanionInventoryMenu fromNetwork(int containerId, Inventory inventory, FriendlyByteBuf buffer) {
        var entity = inventory.player.level().getEntity(buffer.readVarInt());
        return new CompanionInventoryMenu(containerId, inventory,
                entity instanceof ElvenCompanionEntity companion ? companion : null);
    }

    @Override
    public boolean stillValid(Player player) {
        return companion != null && companion.isAlive() && player.getUUID().equals(companion.ownerUuid())
                && player.distanceToSqr(companion) <= 64.0D;
    }

    @Override
    public ItemStack quickMoveStack(Player player, int index) {
        Slot slot = slots.get(index);
        if (!slot.hasItem()) return ItemStack.EMPTY;
        ItemStack present = slot.getItem();
        ItemStack copy = present.copy();
        if (index < COMPANION_SLOTS) {
            if (!moveItemStackTo(present, COMPANION_SLOTS, slots.size(), true)) return ItemStack.EMPTY;
        } else if (!moveItemStackTo(present, 0, COMPANION_SLOTS, false)) {
            return ItemStack.EMPTY;
        }
        if (present.isEmpty()) slot.set(ItemStack.EMPTY); else slot.setChanged();
        return copy;
    }

    @Override
    public void removed(Player player) {
        super.removed(player);
        container.stopOpen(player);
    }
}

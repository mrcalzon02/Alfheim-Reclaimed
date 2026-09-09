package com.continuityworks.leyworks;

import net.minecraft.core.BlockPos;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.world.Container;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.ContainerData;
import net.minecraft.world.inventory.SimpleContainerData;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.ItemStack;

public final class MannaStoneStorageMenu extends AbstractContainerMenu {
    public static final int COLUMNS = 18;
    public static final int ROWS = 6;
    public static final int STORAGE_SLOTS = COLUMNS * ROWS;
    private final Container storage;
    private final ContainerData data;

    public MannaStoneStorageMenu(int id, Inventory inventory, Container storage, ContainerData data) {
        super(Leyworks.MANNA_STORAGE_MENU.get(), id);
        this.storage = storage;
        this.data = data;
        checkContainerSize(storage, STORAGE_SLOTS);
        checkContainerDataCount(data, 1);
        storage.startOpen(inventory.player);
        addDataSlots(data);
        for (int row=0; row<ROWS; row++) for (int column=0; column<COLUMNS; column++) {
            int index=column + row*COLUMNS;
            addSlot(new CapacitySlot(storage, index, 8 + column*18, 18 + row*18));
        }
        int playerX=89, playerY=140;
        for (int row=0; row<3; row++) for (int column=0; column<9; column++)
            addSlot(new Slot(inventory, column + row*9 + 9, playerX + column*18, playerY + row*18));
        for (int column=0; column<9; column++)
            addSlot(new Slot(inventory, column, playerX + column*18, playerY + 58));
    }

    public static MannaStoneStorageMenu fromNetwork(int id, Inventory inventory, FriendlyByteBuf buffer) {
        BlockPos pos=buffer.readBlockPos();
        var blockEntity=inventory.player.level().getBlockEntity(pos);
        Container container=blockEntity instanceof Container found
                ? found : new SimpleContainer(STORAGE_SLOTS);
        return new MannaStoneStorageMenu(id, inventory, container, new SimpleContainerData(1));
    }

    public int activeSlots() { return Math.max(0, Math.min(STORAGE_SLOTS, data.get(0))); }
    public int chestEquivalents() { return (activeSlots() + MannaStoneStorageBlockEntity.CHEST_SLOTS - 1) / MannaStoneStorageBlockEntity.CHEST_SLOTS; }
    public boolean isStorageSlotActive(int index) { return index >= 0 && index < activeSlots(); }

    @Override public boolean stillValid(Player player) { return storage.stillValid(player); }

    @Override public ItemStack quickMoveStack(Player player, int index) {
        Slot slot=slots.get(index);
        if (!slot.hasItem()) return ItemStack.EMPTY;
        ItemStack present=slot.getItem(), copy=present.copy();
        if (index < STORAGE_SLOTS) {
            if (!moveItemStackTo(present, STORAGE_SLOTS, slots.size(), true)) return ItemStack.EMPTY;
        } else if (!moveItemStackTo(present, 0, activeSlots(), false)) return ItemStack.EMPTY;
        if (present.isEmpty()) slot.set(ItemStack.EMPTY); else slot.setChanged();
        return copy;
    }

    @Override public void removed(Player player) {
        super.removed(player);
        storage.stopOpen(player);
    }

    private final class CapacitySlot extends Slot {
        private CapacitySlot(Container container, int index, int x, int y) { super(container,index,x,y); }
        @Override public boolean mayPlace(ItemStack stack) { return isStorageSlotActive(getSlotIndex()); }
        @Override public boolean mayPickup(Player player) { return isStorageSlotActive(getSlotIndex()); }
        @Override public boolean isActive() { return isStorageSlotActive(getSlotIndex()); }
    }
}

package com.continuityworks.leyworks;

import net.minecraft.core.BlockPos;
import net.minecraft.core.NonNullList;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.world.ContainerHelper;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.ContainerData;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.Containers;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BaseContainerBlockEntity;
import net.minecraft.world.level.block.state.BlockState;

public final class MannaStoneStorageBlockEntity extends BaseContainerBlockEntity {
    public static final int CHEST_SLOTS = 27;
    public static final int MAX_GEMS = 3;
    public static final int MAX_SLOTS = CHEST_SLOTS * (MAX_GEMS + 1);
    private NonNullList<ItemStack> items = NonNullList.withSize(MAX_SLOTS, ItemStack.EMPTY);
    private NonNullList<ItemStack> installedGems = NonNullList.withSize(MAX_GEMS, ItemStack.EMPTY);

    private final ContainerData data = new ContainerData() {
        @Override public int get(int index) { return index == 0 ? activeSlots() : 0; }
        @Override public void set(int index, int value) { }
        @Override public int getCount() { return 1; }
    };

    public MannaStoneStorageBlockEntity(BlockPos pos, BlockState state) {
        super(Leyworks.MANNA_STORAGE_ENTITY.get(), pos, state);
    }

    public int gemCount() {
        int count = 0;
        for (ItemStack gem : installedGems) if (!gem.isEmpty()) count++;
        return count;
    }

    public int activeSlots() { return CHEST_SLOTS * (gemCount() + 1); }

    public void installGem(ItemStack gem) {
        int count = gemCount();
        if (count >= MAX_GEMS || gem.isEmpty()) return;
        installedGems.set(count, gem.copyWithCount(1));
        setChanged();
        if (level != null) {
            level.setBlock(worldPosition, getBlockState().setValue(MannaStoneStorageBlock.GEMS, count + 1), 3);
        }
    }

    public void dropInstalledGems(Level level, BlockPos pos) {
        for (ItemStack gem : installedGems) {
            if (!gem.isEmpty()) Containers.dropItemStack(level, pos.getX()+.5, pos.getY()+.75, pos.getZ()+.5, gem.copy());
        }
        installedGems.clear();
    }

    @Override protected Component getDefaultName() {
        return Component.translatable("container.alfheim_leyworks.manna_stone_storage");
    }

    @Override protected AbstractContainerMenu createMenu(int id, Inventory inventory) {
        return new MannaStoneStorageMenu(id, inventory, this, data);
    }

    @Override public int getContainerSize() { return MAX_SLOTS; }
    @Override public boolean isEmpty() {
        for (ItemStack stack : items) if (!stack.isEmpty()) return false;
        return true;
    }
    @Override public ItemStack getItem(int slot) { return items.get(slot); }
    @Override public ItemStack removeItem(int slot, int amount) {
        ItemStack removed=ContainerHelper.removeItem(items,slot,amount);
        if (!removed.isEmpty()) setChanged();
        return removed;
    }
    @Override public ItemStack removeItemNoUpdate(int slot) {
        return ContainerHelper.takeItem(items,slot);
    }
    @Override public void setItem(int slot, ItemStack stack) {
        items.set(slot,stack);
        if (stack.getCount()>getMaxStackSize()) stack.setCount(getMaxStackSize());
        setChanged();
    }
    @Override public void clearContent() {
        items.clear();
        setChanged();
    }

    @Override public boolean canPlaceItem(int slot, ItemStack stack) { return slot < activeSlots(); }

    @Override public boolean stillValid(Player player) {
        return level != null && level.getBlockEntity(worldPosition) == this
                && player.distanceToSqr(worldPosition.getX() + .5, worldPosition.getY() + .5, worldPosition.getZ() + .5) <= 64;
    }

    @Override protected void saveAdditional(CompoundTag tag) {
        super.saveAdditional(tag);
        ContainerHelper.saveAllItems(tag, items);
        CompoundTag upgrades = new CompoundTag();
        ContainerHelper.saveAllItems(upgrades, installedGems);
        tag.put("InstalledGems", upgrades);
    }

    @Override public void load(CompoundTag tag) {
        super.load(tag);
        items = NonNullList.withSize(MAX_SLOTS, ItemStack.EMPTY);
        ContainerHelper.loadAllItems(tag, items);
        installedGems = NonNullList.withSize(MAX_GEMS, ItemStack.EMPTY);
        if (tag.contains("InstalledGems")) ContainerHelper.loadAllItems(tag.getCompound("InstalledGems"), installedGems);
    }
}

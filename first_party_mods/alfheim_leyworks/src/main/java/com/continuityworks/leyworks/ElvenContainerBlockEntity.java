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
import net.minecraft.world.level.block.entity.BaseContainerBlockEntity;
import net.minecraft.world.level.block.state.BlockState;

public final class ElvenContainerBlockEntity extends BaseContainerBlockEntity {
    private NonNullList<ItemStack> items=NonNullList.withSize(MannaStoneStorageMenu.STORAGE_SLOTS,ItemStack.EMPTY);
    private final ContainerData data=new ContainerData(){
        @Override public int get(int index){return index==0?capacity():0;}
        @Override public void set(int index,int value){}
        @Override public int getCount(){return 1;}
    };
    public ElvenContainerBlockEntity(BlockPos pos,BlockState state){super(Leyworks.ELVEN_CONTAINER_ENTITY.get(),pos,state);}
    public int capacity(){return getBlockState().getBlock() instanceof ElvenContainerBlock block?block.style().capacity():0;}
    @Override protected Component getDefaultName(){return getBlockState().getBlock().getName();}
    @Override protected AbstractContainerMenu createMenu(int id,Inventory inventory){return new MannaStoneStorageMenu(id,inventory,this,data);}
    @Override public int getContainerSize(){return MannaStoneStorageMenu.STORAGE_SLOTS;}
    @Override public boolean isEmpty(){for(ItemStack stack:items)if(!stack.isEmpty())return false;return true;}
    @Override public ItemStack getItem(int slot){return items.get(slot);}
    @Override public ItemStack removeItem(int slot,int amount){ItemStack out=ContainerHelper.removeItem(items,slot,amount);if(!out.isEmpty())setChanged();return out;}
    @Override public ItemStack removeItemNoUpdate(int slot){return ContainerHelper.takeItem(items,slot);}
    @Override public void setItem(int slot,ItemStack stack){items.set(slot,stack);if(stack.getCount()>getMaxStackSize())stack.setCount(getMaxStackSize());setChanged();}
    @Override public void clearContent(){items.clear();setChanged();}
    @Override public boolean canPlaceItem(int slot,ItemStack stack){return slot<capacity();}
    @Override public boolean stillValid(Player player){return level!=null&&level.getBlockEntity(worldPosition)==this&&player.distanceToSqr(worldPosition.getX()+.5,worldPosition.getY()+.5,worldPosition.getZ()+.5)<=64;}
    @Override protected void saveAdditional(CompoundTag tag){super.saveAdditional(tag);ContainerHelper.saveAllItems(tag,items);}
    @Override public void load(CompoundTag tag){super.load(tag);items=NonNullList.withSize(MannaStoneStorageMenu.STORAGE_SLOTS,ItemStack.EMPTY);ContainerHelper.loadAllItems(tag,items);}
}

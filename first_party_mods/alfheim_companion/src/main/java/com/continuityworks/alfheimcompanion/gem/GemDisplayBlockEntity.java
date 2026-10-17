package com.continuityworks.alfheimcompanion.gem;

import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;

public final class GemDisplayBlockEntity extends BlockEntity {
    private ItemStack sample=ItemStack.EMPTY;
    public GemDisplayBlockEntity(BlockPos pos,BlockState state){super(ModGemDisplays.DISPLAY.get(),pos,state);}
    public ItemStack sample(){return sample;}
    public void setSample(ItemStack stack){sample=stack.isEmpty()?ItemStack.EMPTY:stack.copyWithCount(1);setChanged();if(level!=null)level.sendBlockUpdated(worldPosition,getBlockState(),getBlockState(),3);}
    public Component label(){var entry=ModGemDisplays.find(sample);return entry==null?sample.getHoverName():Component.literal(entry.name());}
    @Override protected void saveAdditional(CompoundTag tag){super.saveAdditional(tag);tag.put("Sample",sample.save(new CompoundTag()));}
    @Override public void load(CompoundTag tag){super.load(tag);sample=ItemStack.of(tag.getCompound("Sample"));if(!sample.isEmpty())sample.setCount(1);}
    @Override public CompoundTag getUpdateTag(){return saveWithoutMetadata();}
    @Override public ClientboundBlockEntityDataPacket getUpdatePacket(){return ClientboundBlockEntityDataPacket.create(this);}
    @Override public AABB getRenderBoundingBox(){return new AABB(worldPosition).expandTowards(0,1,0);}
}

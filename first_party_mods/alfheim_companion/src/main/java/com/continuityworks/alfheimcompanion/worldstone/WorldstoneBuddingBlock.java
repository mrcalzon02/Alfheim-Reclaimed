package com.continuityworks.alfheimcompanion.worldstone;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.material.Fluids;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.*;
import net.minecraft.world.level.BlockGetter;
import java.util.List;

/** Vanilla-style slow, loaded-chunk-only crystal growth on all six exposed faces. */
public final class WorldstoneBuddingBlock extends Block {
    public WorldstoneBuddingBlock(Properties properties){super(properties.randomTicks());}
    @Override public void appendHoverText(ItemStack stack,BlockGetter world,List<Component> lines,TooltipFlag flag) {
        lines.add(Component.literal("Grows harvestable Worldstone Crystal Clusters on exposed faces."));
        lines.add(Component.literal("Breaking destroys this budding source; Silk Touch cannot collect it."));
    }
    @Override public void randomTick(BlockState state,ServerLevel level,BlockPos pos,RandomSource random) {
        if(random.nextInt(5)==0)grow(level,pos,Direction.getRandom(random));
    }
    public static boolean grow(ServerLevel level,BlockPos source,Direction direction) {
        if(!level.getBlockState(source).is(ModWorldstoneBlocks.CRYSTAL.get()))return false;
        var pos=source.relative(direction);if(!level.hasChunkAt(pos))return false;
        var old=level.getBlockState(pos);Block next=null;
        if(old.isAir() || old.is(Blocks.WATER) && old.getFluidState().getAmount()==8)next=ModWorldstoneBlocks.SMALL.get();
        else if(old.hasProperty(AmethystClusterBlock.FACING) && old.getValue(AmethystClusterBlock.FACING)==direction) {
            if(old.is(ModWorldstoneBlocks.SMALL.get()))next=ModWorldstoneBlocks.MEDIUM.get();
            else if(old.is(ModWorldstoneBlocks.MEDIUM.get()))next=ModWorldstoneBlocks.LARGE.get();
            else if(old.is(ModWorldstoneBlocks.LARGE.get()))next=ModWorldstoneBlocks.CLUSTER.get();
        }
        if(next==null)return false;
        var state=next.defaultBlockState().setValue(AmethystClusterBlock.FACING,direction)
            .setValue(AmethystClusterBlock.WATERLOGGED,old.getFluidState().getType()==Fluids.WATER);
        level.setBlockAndUpdate(pos,state);return true;
    }
}

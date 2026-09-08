package com.continuityworks.leyworks;

import net.minecraft.core.BlockPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.state.BlockState;
import org.jetbrains.annotations.Nullable;

/** The active node. All behaviour lives in the block entity; this only wires the ticker. */
public class LeyConduitNodeBlock extends Block implements EntityBlock {

    public LeyConduitNodeBlock(Properties properties) {
        super(properties);
    }

    @Override
    public @Nullable BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new LeyConduitNodeBlockEntity(pos, state);
    }

    @Override
    public <T extends BlockEntity> @Nullable BlockEntityTicker<T> getTicker(
            Level level, BlockState state, net.minecraft.world.level.block.entity.BlockEntityType<T> type) {
        // Server ticks do the pyramid read and the aura; the client tick only draws particles.
        return type != Leyworks.NODE_ENTITY.get() ? null
                : (lvl, pos, st, be) -> LeyConduitNodeBlockEntity.tick(
                        lvl, pos, st, (LeyConduitNodeBlockEntity) be);
    }
}

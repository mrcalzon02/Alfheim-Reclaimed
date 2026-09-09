package com.continuityworks.leyworks;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.Containers;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.BaseEntityBlock;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.DirectionProperty;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;
import net.minecraftforge.network.NetworkHooks;
import org.jetbrains.annotations.Nullable;

/** Fixed-capacity cultural storage. Shape and honest inventory size are selected by style. */
public final class ElvenContainerBlock extends BaseEntityBlock {
    public static final DirectionProperty FACING=BlockStateProperties.HORIZONTAL_FACING;

    public enum Style {
        ROYAL_CHEST(54, box(1,0,2,15,14,14)),
        GEMSTONE_COFFER(18, box(2,0,3,14,9,13)),
        DREAMWOOD_CRATE(27, box(1,0,1,15,15,15)),
        PROVISION_CRATE(27, box(1,0,1,15,15,15)),
        SCROLL_CRATE(27, box(1,0,1,15,13,15)),
        TALL_VASE(9, box(4,0,4,12,16,12)),
        MEMORIAL_URN(9, box(4,0,4,12,14,12));

        private final int capacity;
        private final VoxelShape shape;
        Style(int capacity,VoxelShape shape){this.capacity=capacity;this.shape=shape;}
        public int capacity(){return capacity;}
        public VoxelShape shape(){return shape;}
    }

    private final Style style;
    public ElvenContainerBlock(Properties properties,Style style){
        super(properties);this.style=style;
        registerDefaultState(stateDefinition.any().setValue(FACING,Direction.NORTH));
    }
    public Style style(){return style;}
    @Override protected void createBlockStateDefinition(StateDefinition.Builder<net.minecraft.world.level.block.Block,BlockState> builder){builder.add(FACING);}
    @Override public @Nullable BlockState getStateForPlacement(BlockPlaceContext context){return defaultBlockState().setValue(FACING,context.getHorizontalDirection().getOpposite());}
    @Override public RenderShape getRenderShape(BlockState state){return RenderShape.MODEL;}
    @Override public VoxelShape getShape(BlockState state,BlockGetter level,BlockPos pos,CollisionContext context){return style.shape();}
    @Override public @Nullable BlockEntity newBlockEntity(BlockPos pos,BlockState state){return new ElvenContainerBlockEntity(pos,state);}

    @Override public InteractionResult use(BlockState state,Level level,BlockPos pos,Player player,InteractionHand hand,BlockHitResult hit){
        if(!level.isClientSide && player instanceof ServerPlayer server && level.getBlockEntity(pos) instanceof ElvenContainerBlockEntity storage)
            NetworkHooks.openScreen(server,storage,pos);
        return InteractionResult.sidedSuccess(level.isClientSide);
    }
    @Override public void onRemove(BlockState state,Level level,BlockPos pos,BlockState next,boolean moving){
        if(!state.is(next.getBlock())){
            if(level.getBlockEntity(pos) instanceof ElvenContainerBlockEntity storage) Containers.dropContents(level,pos,storage);
            super.onRemove(state,level,pos,next,moving);
        }
    }
    @Override public boolean hasAnalogOutputSignal(BlockState state){return true;}
    @Override public int getAnalogOutputSignal(BlockState state,Level level,BlockPos pos){
        return level.getBlockEntity(pos) instanceof ElvenContainerBlockEntity storage
                ? net.minecraft.world.inventory.AbstractContainerMenu.getRedstoneSignalFromContainer(storage):0;
    }
}

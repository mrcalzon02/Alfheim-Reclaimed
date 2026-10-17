package com.continuityworks.alfheimcompanion.fey;

import net.minecraft.core.*;
import net.minecraft.world.item.*;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.entity.*;
import net.minecraft.world.level.block.state.*;
import net.minecraft.world.level.block.state.properties.*;
import net.minecraft.world.level.storage.loot.LootParams;
import net.minecraft.world.level.storage.loot.parameters.LootContextParams;
import java.util.*;

/** A bark apartment with bee-style residents; its dropped item retains their complete NBT. */
public final class FeyHomeBlock extends BaseEntityBlock {
    public static final DirectionProperty FACING=HorizontalDirectionalBlock.FACING;
    public final String season;
    public FeyHomeBlock(String season){super(Properties.of().mapColor(net.minecraft.world.level.material.MapColor.WOOD).strength(2.5F).sound(SoundType.WOOD).noOcclusion());this.season=season;registerDefaultState(stateDefinition.any().setValue(FACING,Direction.NORTH));}
    @Override protected void createBlockStateDefinition(StateDefinition.Builder<Block,BlockState> b){b.add(FACING);}
    @Override public BlockState getStateForPlacement(BlockPlaceContext c){return defaultBlockState().setValue(FACING,c.getHorizontalDirection().getOpposite());}
    @Override public BlockState rotate(BlockState s,Rotation r){return s.setValue(FACING,r.rotate(s.getValue(FACING)));}
    @Override public BlockState mirror(BlockState s,Mirror m){return rotate(s,m.getRotation(s.getValue(FACING)));}
    @Override public RenderShape getRenderShape(BlockState state){return RenderShape.MODEL;}
    @Override public BlockEntity newBlockEntity(BlockPos pos,BlockState state){return new FeyHomeBlockEntity(pos,state);}
    @Override public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level level,BlockState state,BlockEntityType<T> type){return level.isClientSide?null:createTickerHelper(type,ModFeyHomes.HOME.get(),FeyHomeBlockEntity::tick);}
    @Override public List<ItemStack> getDrops(BlockState state,LootParams.Builder builder){
        ItemStack stack=new ItemStack(this);var be=builder.getOptionalParameter(LootContextParams.BLOCK_ENTITY);
        if(be instanceof FeyHomeBlockEntity home)BlockItem.setBlockEntityData(stack,ModFeyHomes.HOME.get(),home.saveWithoutMetadata());
        return List.of(stack);
    }
    @Override public void playerWillDestroy(Level level,BlockPos pos,BlockState state,net.minecraft.world.entity.player.Player player){
        if(!level.isClientSide&&player.isCreative()&&level.getBlockEntity(pos) instanceof FeyHomeBlockEntity home&&home.occupied()>0){
            ItemStack stack=new ItemStack(this);BlockItem.setBlockEntityData(stack,ModFeyHomes.HOME.get(),home.saveWithoutMetadata());popResource(level,pos,stack);
        }
        super.playerWillDestroy(level,pos,state,player);
    }
}

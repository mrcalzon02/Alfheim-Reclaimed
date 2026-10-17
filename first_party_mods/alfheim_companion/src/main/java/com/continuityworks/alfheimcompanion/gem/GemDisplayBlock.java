package com.continuityworks.alfheimcompanion.gem;

import net.minecraft.core.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.*;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.entity.*;
import net.minecraft.world.level.block.state.*;
import net.minecraft.world.level.block.state.properties.DirectionProperty;
import net.minecraft.world.level.storage.loot.LootParams;
import net.minecraft.world.level.storage.loot.parameters.LootContextParams;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.*;
import net.minecraftforge.registries.ForgeRegistries;
import java.util.*;

public final class GemDisplayBlock extends BaseEntityBlock {
    public static final DirectionProperty FACING=HorizontalDirectionalBlock.FACING;
    public GemDisplayBlock(){super(Properties.of().mapColor(net.minecraft.world.level.material.MapColor.QUARTZ).strength(2).sound(SoundType.STONE).noOcclusion());registerDefaultState(stateDefinition.any().setValue(FACING,Direction.NORTH));}
    @Override protected void createBlockStateDefinition(StateDefinition.Builder<Block,BlockState> b){b.add(FACING);}
    @Override public BlockState getStateForPlacement(BlockPlaceContext c){return c.getLevel().getBlockState(c.getClickedPos().above()).canBeReplaced(c)?defaultBlockState().setValue(FACING,c.getHorizontalDirection().getOpposite()):null;}
    @Override public BlockState rotate(BlockState state,Rotation r){return state.setValue(FACING,r.rotate(state.getValue(FACING)));}
    @Override public BlockState mirror(BlockState state,Mirror m){return rotate(state,m.getRotation(state.getValue(FACING)));}
    @Override public RenderShape getRenderShape(BlockState state){return RenderShape.MODEL;}
    @Override public VoxelShape getShape(BlockState s,BlockGetter l,BlockPos p,CollisionContext c){return Block.box(1,0,1,15,26,15);}
    @Override public BlockEntity newBlockEntity(BlockPos p,BlockState s){return new GemDisplayBlockEntity(p,s);}
    @Override public void setPlacedBy(Level level,BlockPos pos,BlockState state,LivingEntity placer,ItemStack stack){
        if(!level.isClientSide&&stack.getItem() instanceof ModGemDisplays.SampleItem sample&&level.getBlockEntity(pos) instanceof GemDisplayBlockEntity display){
            var item=ForgeRegistries.ITEMS.getValue(new ResourceLocation(sample.entry.item()));if(item!=null&&item!=Items.AIR)display.setSample(new ItemStack(item));
        }
    }
    @Override public InteractionResult use(BlockState state,Level level,BlockPos pos,Player player,InteractionHand hand,BlockHitResult hit){
        if(!(level.getBlockEntity(pos) instanceof GemDisplayBlockEntity display))return InteractionResult.PASS;
        var held=player.getItemInHand(hand);
        if(held.isEmpty()&&player.isShiftKeyDown()&&!display.sample().isEmpty()){
            if(!level.isClientSide){var gem=display.sample().copy();display.setSample(ItemStack.EMPTY);if(!player.addItem(gem))player.drop(gem,false);}
            return InteractionResult.sidedSuccess(level.isClientSide);
        }
        if(display.sample().isEmpty()&&ModGemDisplays.find(held)!=null){
            if(!level.isClientSide){display.setSample(held.copyWithCount(1));if(!player.getAbilities().instabuild)held.shrink(1);}
            return InteractionResult.sidedSuccess(level.isClientSide);
        }
        if(!level.isClientSide&&!display.sample().isEmpty())player.displayClientMessage(display.label(),true);
        return display.sample().isEmpty()?InteractionResult.PASS:InteractionResult.sidedSuccess(level.isClientSide);
    }
    @Override public List<ItemStack> getDrops(BlockState state,LootParams.Builder builder){
        var drops=new ArrayList<ItemStack>();drops.add(new ItemStack(ModGemDisplays.EMPTY.get()));
        if(builder.getOptionalParameter(LootContextParams.BLOCK_ENTITY) instanceof GemDisplayBlockEntity display&&!display.sample().isEmpty())drops.add(display.sample().copy());
        return drops;
    }
}

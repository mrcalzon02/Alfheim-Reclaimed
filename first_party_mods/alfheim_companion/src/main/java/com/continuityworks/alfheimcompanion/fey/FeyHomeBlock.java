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
    public static final IntegerProperty DUST_LEVEL=IntegerProperty.create("dust_level",0,5);
    public final String season;
    public FeyHomeBlock(String season){super(Properties.of().mapColor(net.minecraft.world.level.material.MapColor.WOOD).strength(2.5F).sound(SoundType.WOOD).noOcclusion());this.season=season;registerDefaultState(stateDefinition.any().setValue(FACING,Direction.NORTH).setValue(DUST_LEVEL,0));}
    @Override protected void createBlockStateDefinition(StateDefinition.Builder<Block,BlockState> b){b.add(FACING,DUST_LEVEL);}
    @Override public BlockState getStateForPlacement(BlockPlaceContext c){return defaultBlockState().setValue(FACING,c.getHorizontalDirection().getOpposite());}
    @Override public BlockState rotate(BlockState s,Rotation r){return s.setValue(FACING,r.rotate(s.getValue(FACING)));}
    @Override public BlockState mirror(BlockState s,Mirror m){return rotate(s,m.getRotation(s.getValue(FACING)));}
    @Override public RenderShape getRenderShape(BlockState state){return RenderShape.MODEL;}
    @Override public BlockEntity newBlockEntity(BlockPos pos,BlockState state){return new FeyHomeBlockEntity(pos,state);}
    @Override public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level level,BlockState state,BlockEntityType<T> type){return level.isClientSide?null:createTickerHelper(type,ModFeyHomes.HOME.get(),FeyHomeBlockEntity::tick);}
    @Override public net.minecraft.world.InteractionResult use(BlockState state,Level level,BlockPos pos,net.minecraft.world.entity.player.Player player,net.minecraft.world.InteractionHand hand,net.minecraft.world.phys.BlockHitResult hit){
        ItemStack tool=player.getItemInHand(hand);
        boolean shears=tool.canPerformAction(net.minecraftforge.common.ToolActions.SHEARS_HARVEST);
        if(!shears&&!tool.isEmpty())return net.minecraft.world.InteractionResult.PASS;
        if(!level.isClientSide&&level.getBlockEntity(pos) instanceof FeyHomeBlockEntity home){
            if(shears&&home.dustLevel()==5){
                var dust=net.minecraftforge.registries.ForgeRegistries.ITEMS.getValue(new net.minecraft.resources.ResourceLocation("botania","pixie_dust"));
                if(dust!=null&&dust!=Items.AIR){
                    Item usedTool=tool.getItem();
                    home.harvestDust();popResource(level,pos,new ItemStack(dust,3));
                    level.playSound(null,pos,net.minecraft.sounds.SoundEvents.BEEHIVE_SHEAR,net.minecraft.sounds.SoundSource.BLOCKS,1,1);
                    level.gameEvent(player,net.minecraft.world.level.gameevent.GameEvent.SHEAR,pos);
                    if(!player.getAbilities().instabuild)tool.hurtAndBreak(1,player,p->p.broadcastBreakEvent(hand));
                    player.awardStat(net.minecraft.stats.Stats.ITEM_USED.get(usedTool));
                }
            }else player.displayClientMessage(net.minecraft.network.chat.Component.translatable(home.dustLevel()==5?"message.alfheim_companion.fey_dust_ready":"message.alfheim_companion.fey_dust_progress",home.dustLevel()),true);
        }
        return net.minecraft.world.InteractionResult.sidedSuccess(level.isClientSide);
    }
    @Override public boolean hasAnalogOutputSignal(BlockState state){return true;}
    @Override public int getAnalogOutputSignal(BlockState state,Level level,BlockPos pos){return state.getValue(DUST_LEVEL);}
    @Override public void animateTick(BlockState state,Level level,BlockPos pos,net.minecraft.util.RandomSource random){
        if(state.getValue(DUST_LEVEL)==5&&random.nextInt(4)==0){var d=state.getValue(FACING);level.addParticle(net.minecraft.core.particles.ParticleTypes.END_ROD,pos.getX()+.5+d.getStepX()*.6,pos.getY()+.4+random.nextDouble()*.4,pos.getZ()+.5+d.getStepZ()*.6,0,.01,0);}
    }
    @Override public List<ItemStack> getDrops(BlockState state,LootParams.Builder builder){
        ItemStack stack=new ItemStack(this);var be=builder.getOptionalParameter(LootContextParams.BLOCK_ENTITY);
        if(be instanceof FeyHomeBlockEntity home)BlockItem.setBlockEntityData(stack,ModFeyHomes.HOME.get(),home.saveWithoutMetadata());
        return List.of(stack);
    }
    @Override public void playerWillDestroy(Level level,BlockPos pos,BlockState state,net.minecraft.world.entity.player.Player player){
        if(!level.isClientSide&&player.isCreative()&&level.getBlockEntity(pos) instanceof FeyHomeBlockEntity home&&(home.occupied()>0||home.dustLevel()>0)){
            ItemStack stack=new ItemStack(this);BlockItem.setBlockEntityData(stack,ModFeyHomes.HOME.get(),home.saveWithoutMetadata());popResource(level,pos,stack);
        }
        super.playerWillDestroy(level,pos,state,player);
    }
}

package com.continuityworks.leyworks;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.util.StringRepresentable;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;
import org.jetbrains.annotations.Nullable;

/** Pure scenery, including one-item two-part furniture. No entity, inventory or ticker. */
public final class ElvenDecorBlock extends HorizontalDirectionalBlock {
    public enum Kind {FLOOR,WALL,TALL,SOFA}
    public enum Part implements StringRepresentable {
        BASE,EXTENSION;
        @Override public String getSerializedName(){return name().toLowerCase(java.util.Locale.ROOT);}
    }
    public static final EnumProperty<Part> PART=EnumProperty.create("part",Part.class);
    private final Kind kind;
    private final VoxelShape[][] shapes;
    public ElvenDecorBlock(Properties properties,ElvenDecorDefinitions.Definition definition) {
        super(properties);kind=definition.kind();shapes=new VoxelShape[][]{DistrictStationBlock.rotations(definition.base()),DistrictStationBlock.rotations(definition.extension())};
        registerDefaultState(stateDefinition.any().setValue(FACING,Direction.NORTH).setValue(PART,Part.BASE));
    }
    Kind kind(){return kind;}
    boolean assembled(){return kind==Kind.TALL||kind==Kind.SOFA;}
    private Direction offset(BlockState state){return kind==Kind.TALL?Direction.UP:state.getValue(FACING).getClockWise();}
    private boolean matches(BlockState candidate,BlockState state,Part part){return candidate.is(this)&&candidate.getValue(PART)==part&&candidate.getValue(FACING)==state.getValue(FACING);}
    @Override protected void createBlockStateDefinition(StateDefinition.Builder<Block,BlockState> builder){builder.add(FACING,PART);}
    @Override public @Nullable BlockState getStateForPlacement(BlockPlaceContext context) {
        var level=context.getLevel();var pos=context.getClickedPos();var facing=context.getHorizontalDirection().getOpposite();
        if(kind==Kind.WALL){facing=context.getClickedFace();if(facing.getAxis().isVertical())return null;}
        var state=defaultBlockState().setValue(FACING,facing);
        if(!canSurvive(state,level,pos))return null;
        if(assembled()) {
            var other=pos.relative(offset(state));
            if(level.isOutsideBuildHeight(other)||!level.getBlockState(other).canBeReplaced(context))return null;
            if(kind==Kind.SOFA&&!level.getBlockState(other.below()).isFaceSturdy(level,other.below(),Direction.UP))return null;
        }
        return state;
    }
    @Override public void setPlacedBy(Level level,BlockPos pos,BlockState state,@Nullable LivingEntity entity,ItemStack stack) {
        if(!level.isClientSide&&assembled())level.setBlock(pos.relative(offset(state)),state.setValue(PART,Part.EXTENSION),3);
    }
    @Override public boolean canSurvive(BlockState state,LevelReader level,BlockPos pos) {
        if(kind==Kind.WALL){var behind=pos.relative(state.getValue(FACING).getOpposite());return level.getBlockState(behind).isFaceSturdy(level,behind,state.getValue(FACING));}
        if(assembled()&&state.getValue(PART)==Part.EXTENSION) {
            if(!matches(level.getBlockState(pos.relative(offset(state).getOpposite())),state,Part.BASE))return false;
            if(kind==Kind.TALL)return true;
        }
        return level.getBlockState(pos.below()).isFaceSturdy(level,pos.below(),Direction.UP);
    }
    @Override public BlockState updateShape(BlockState state,Direction direction,BlockState neighbor,LevelAccessor level,BlockPos pos,BlockPos other) {
        if(!canSurvive(state,level,pos))return Blocks.AIR.defaultBlockState();
        if(assembled()) {
            var connection=state.getValue(PART)==Part.BASE?offset(state):offset(state).getOpposite();
            var partner=state.getValue(PART)==Part.BASE?Part.EXTENSION:Part.BASE;
            if(direction==connection&&!matches(neighbor,state,partner))return Blocks.AIR.defaultBlockState();
        }
        return super.updateShape(state,direction,neighbor,level,pos,other);
    }
    @Override public void playerWillDestroy(Level level,BlockPos pos,BlockState state,Player player) {
        if(!level.isClientSide&&player.isCreative()&&assembled()&&state.getValue(PART)==Part.EXTENSION) {
            var base=pos.relative(offset(state).getOpposite());
            if(matches(level.getBlockState(base),state,Part.BASE))level.setBlock(base,Blocks.AIR.defaultBlockState(),35);
        }
        super.playerWillDestroy(level,pos,state,player);
    }
    @Override public BlockState rotate(BlockState state,Rotation rotation){return state.setValue(FACING,rotation.rotate(state.getValue(FACING)));}
    @Override public BlockState mirror(BlockState state,Mirror mirror){
        var result=rotate(state,mirror.getRotation(state.getValue(FACING)));
        // Reflection reverses a sofa's handedness as well as its facing.
        return kind==Kind.SOFA&&mirror!=Mirror.NONE?result.cycle(PART):result;
    }
    @Override public VoxelShape getShape(BlockState state,BlockGetter level,BlockPos pos,CollisionContext collision){return shapes[state.getValue(PART).ordinal()][state.getValue(FACING).get2DDataValue()];}
}

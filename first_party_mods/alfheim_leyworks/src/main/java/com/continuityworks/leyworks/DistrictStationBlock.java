package com.continuityworks.leyworks;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.SimpleMenuProvider;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.*;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

/** Familiar vanilla processing with custom-block validity and no ticking block entity. */
public final class DistrictStationBlock extends HorizontalDirectionalBlock {
    public enum Kind {
        CRAFT("district_artificer_desk",DistrictFurnishingShapes.ARTIFICER_DESK),
        STONECUT("district_masons_bench",DistrictFurnishingShapes.MASONS_BENCH),
        LOOM("district_weaving_frame",DistrictFurnishingShapes.WEAVING_FRAME),
        CARTOGRAPHY("district_cartographers_table",DistrictFurnishingShapes.CARTOGRAPHERS_TABLE),
        GRINDSTONE("district_mending_bench",DistrictFurnishingShapes.MENDING_BENCH);
        final String id; final VoxelShape shape;
        Kind(String id,VoxelShape shape){this.id=id;this.shape=shape;}
    }
    private final Kind kind;
    private final VoxelShape[] shapes;
    public DistrictStationBlock(Properties properties,Kind kind) {
        super(properties);this.kind=kind;this.shapes=rotations(kind.shape);
        registerDefaultState(stateDefinition.any().setValue(FACING,Direction.NORTH));
    }
    @Override protected void createBlockStateDefinition(StateDefinition.Builder<Block,BlockState> builder){builder.add(FACING);}
    @Override public BlockState getStateForPlacement(BlockPlaceContext context){return defaultBlockState().setValue(FACING,context.getHorizontalDirection().getOpposite());}
    @Override public BlockState rotate(BlockState state,Rotation rotation){return state.setValue(FACING,rotation.rotate(state.getValue(FACING)));}
    @Override public BlockState mirror(BlockState state,Mirror mirror){return state.rotate(mirror.getRotation(state.getValue(FACING)));}
    @Override public VoxelShape getShape(BlockState state,BlockGetter level,BlockPos pos,CollisionContext collision){return shapes[state.getValue(FACING).get2DDataValue()];}
    static VoxelShape[] rotations(VoxelShape north) {
        var result=new VoxelShape[4];VoxelShape shape=north;
        for(var facing:new Direction[]{Direction.NORTH,Direction.EAST,Direction.SOUTH,Direction.WEST}) {
            result[facing.get2DDataValue()]=shape;
            var turned=new VoxelShape[]{Shapes.empty()};
            shape.forAllBoxes((x,y,z,X,Y,Z)->turned[0]=Shapes.or(turned[0],Shapes.box(1-Z,y,x,1-z,Y,X)));
            shape=turned[0];
        }
        return result;
    }
    private boolean valid(ContainerLevelAccess access,Player player) {
        return access.evaluate((level,pos)->level.getBlockState(pos).is(this)
                &&player.distanceToSqr(pos.getX()+.5,pos.getY()+.5,pos.getZ()+.5)<=64,false);
    }
    AbstractContainerMenu menu(int id,Inventory inventory,ContainerLevelAccess access) {
        // Vanilla menus otherwise require the vanilla block, immediately closing custom furniture.
        return switch(kind) {
            case CRAFT -> new CraftingMenu(id,inventory,access){@Override public boolean stillValid(Player p){return valid(access,p);}};
            case STONECUT -> new StonecutterMenu(id,inventory,access){@Override public boolean stillValid(Player p){return valid(access,p);}};
            case LOOM -> new LoomMenu(id,inventory,access){@Override public boolean stillValid(Player p){return valid(access,p);}};
            case CARTOGRAPHY -> new CartographyTableMenu(id,inventory,access){@Override public boolean stillValid(Player p){return valid(access,p);}};
            case GRINDSTONE -> new GrindstoneMenu(id,inventory,access){@Override public boolean stillValid(Player p){return valid(access,p);}};
        };
    }
    @Override public net.minecraft.world.MenuProvider getMenuProvider(BlockState state,Level level,BlockPos pos) {
        return new SimpleMenuProvider((id,inventory,player)->menu(id,inventory,ContainerLevelAccess.create(level,pos)),getName());
    }
    @Override public InteractionResult use(BlockState state,Level level,BlockPos pos,Player player,InteractionHand hand,BlockHitResult hit) {
        if(!level.isClientSide)player.openMenu(getMenuProvider(state,level,pos));
        return InteractionResult.sidedSuccess(level.isClientSide);
    }
    Kind kind(){return kind;}
}

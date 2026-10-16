package com.continuityworks.leyworks;

import com.mojang.authlib.GameProfile;
import java.util.UUID;
import net.minecraft.commands.Commands;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.*;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.*;
import net.minecraftforge.common.util.FakePlayer;
import net.minecraftforge.common.util.FakePlayerFactory;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Real BlockItem placement and removal in a disposable world, never a player save. */
@Mod.EventBusSubscriber(modid=Leyworks.MOD_ID)
public final class ElvenDecorAudit {
    private static final BlockPos ORIGIN=new BlockPos(2048,192,2048);
    private static final Direction[] FACINGS={Direction.NORTH,Direction.EAST,Direction.SOUTH,Direction.WEST};
    private ElvenDecorAudit() {}
    private static void require(boolean ok,String message){if(!ok)throw new IllegalStateException("DECOR_FAIL "+message);}
    private static ServerLevel level(CommandSourceStack source) {
        require(source.getServer().getWorldData().getLevelName().startsWith("validation-"),"disposable validation world required");return source.getLevel();
    }
    @SubscribeEvent public static void register(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("alfheimdecor").requires(s->s.hasPermission(4))
            .then(Commands.literal("audit").executes(c->{try{return audit(c.getSource());}catch(RuntimeException ex){org.slf4j.LoggerFactory.getLogger(ElvenDecorAudit.class).error("DECOR_FAIL audit",ex);return 0;}}))
            .then(Commands.literal("inspect").executes(c->inspect(c.getSource()))));
    }
    private static BlockPos other(ElvenDecorBlock block,BlockPos pos,Direction facing) {
        return pos.relative(block.kind()==ElvenDecorBlock.Kind.TALL?Direction.UP:facing.getClockWise());
    }
    private static void prepare(ServerLevel level,BlockPos pos) {
        for(int x=-2;x<=2;x++)for(int z=-2;z<=2;z++) {
            for(int y=0;y<=2;y++)level.setBlockAndUpdate(pos.offset(x,y,z),Blocks.AIR.defaultBlockState());
            level.setBlockAndUpdate(pos.offset(x,-1,z),Blocks.STONE.defaultBlockState());
        }
        clearDrops(level,pos);
    }
    private static void clearDrops(ServerLevel level,BlockPos pos) {
        for(var item:level.getEntitiesOfClass(ItemEntity.class,new AABB(pos).inflate(3)))item.discard();
    }
    private static void drops(ServerLevel level,BlockPos pos,Item item,int expected,String context) {
        int count=level.getEntitiesOfClass(ItemEntity.class,new AABB(pos).inflate(3)).stream().filter(e->e.getItem().is(item)).mapToInt(e->e.getItem().getCount()).sum();
        require(count==expected,context+" expected "+expected+" drops, got "+count);clearDrops(level,pos);
    }
    private static BlockPlaceContext context(ServerLevel level,FakePlayer player,ElvenDecorBlock block,BlockPos pos,Direction facing,ItemStack stack) {
        player.setPos(pos.getX()+.5,pos.getY(),pos.getZ()+4);player.setYRot(facing.getOpposite().toYRot());
        BlockPos support=block.kind()==ElvenDecorBlock.Kind.WALL?pos.relative(facing.getOpposite()):pos.below();
        Direction face=block.kind()==ElvenDecorBlock.Kind.WALL?facing:Direction.UP;
        if(block.kind()==ElvenDecorBlock.Kind.WALL)level.setBlockAndUpdate(support,Blocks.STONE.defaultBlockState());
        return new BlockPlaceContext(level,player,InteractionHand.MAIN_HAND,stack,new BlockHitResult(Vec3.atCenterOf(support),face,support,false));
    }
    private static void place(ServerLevel level,FakePlayer player,ElvenDecorBlock block,BlockPos pos,Direction facing) {
        var stack=new ItemStack(block,2);var result=((BlockItem)block.asItem()).place(context(level,player,block,pos,facing,stack));
        require(result.consumesAction()&&stack.getCount()==1,"one-item placement "+block.getDescriptionId()+" "+result+" count="+stack.getCount());
        var state=level.getBlockState(pos);require(state.is(block)&&state.getValue(ElvenDecorBlock.FACING)==facing&&state.getValue(ElvenDecorBlock.PART)==ElvenDecorBlock.Part.BASE,"base/facing");
        require(level.getBlockEntity(pos)==null&&block.getMenuProvider(state,level,pos)==null,"pure decoration");
        if(block.assembled()) {
            var o=other(block,pos,facing);var extension=level.getBlockState(o);
            require(extension.is(block)&&extension.getValue(ElvenDecorBlock.PART)==ElvenDecorBlock.Part.EXTENSION&&extension.getValue(ElvenDecorBlock.FACING)==facing,"assembly partner");
            require(level.getBlockEntity(o)==null,"extension has no ticker/entity");
        }
        var rotated=state;for(int i=0;i<4;i++)rotated=rotated.rotate(Rotation.CLOCKWISE_90);require(rotated==state,"rotation cycle");
    }
    private static int audit(CommandSourceStack source) {
        var level=level(source);var player=FakePlayerFactory.get(level,new GameProfile(UUID.fromString("41e78322-71cb-4188-986c-d35d6b2ef810"),"[ElvenDecorAudit]"));
        player.setGameMode(GameType.SURVIVAL);int index=0,placements=0,assemblies=0,walls=0;
        for(var entry:Leyworks.ELVEN_DECOR.entrySet()) {
            var block=(ElvenDecorBlock)entry.getValue().get();var pos=ORIGIN.offset(index%6*8,0,index/6*8);index++;
            var id=BuiltInRegistries.BLOCK.getKey(block);var recipe=level.getRecipeManager().byKey(id).orElseThrow();
            require(recipe.getResultItem(level.registryAccess()).is(block.asItem())&&recipe.getIngredients().stream().allMatch(i->i.getItems().length>0),"recipe "+id);
            for(var facing:FACINGS) {
                prepare(level,pos);place(level,player,block,pos,facing);placements++;
                level.destroyBlock(pos,true,player);require(!level.getBlockState(pos).is(block),"base removed");
                if(block.assembled())require(!level.getBlockState(other(block,pos,facing)).is(block),"partner cleanup after base break");
                drops(level,pos,block.asItem(),1,id+" base break");
                if(block.assembled()) {
                    prepare(level,pos);place(level,player,block,pos,facing);
                    var o=other(block,pos,facing);level.destroyBlock(o,true,player);
                    require(!level.getBlockState(pos).is(block)&&!level.getBlockState(o).is(block),"partner break cleanup");
                    drops(level,pos,block.asItem(),1,id+" extension break");
                    prepare(level,pos);level.setBlockAndUpdate(o,Blocks.STONE.defaultBlockState());
                    var stack=new ItemStack(block);var result=((BlockItem)block.asItem()).place(context(level,player,block,pos,facing,stack));
                    require(!result.consumesAction()&&stack.getCount()==1&&!level.getBlockState(pos).is(block),"blocked assembly rejection");
                }
                if(block.kind()==ElvenDecorBlock.Kind.WALL) {
                    prepare(level,pos);place(level,player,block,pos,facing);level.destroyBlock(pos.relative(facing.getOpposite()),false);
                    require(!level.getBlockState(pos).is(block),"unsupported wall cleanup");drops(level,pos,block.asItem(),1,id+" wall support");
                }
            }
            if(block.assembled()) {
                prepare(level,pos);place(level,player,block,pos,Direction.NORTH);player.setGameMode(GameType.CREATIVE);
                var o=other(block,pos,Direction.NORTH);block.playerWillDestroy(level,o,level.getBlockState(o),player);level.destroyBlock(o,false,player);
                require(!level.getBlockState(pos).is(block)&&!level.getBlockState(o).is(block),"creative cleanup");drops(level,pos,block.asItem(),0,id+" creative");player.setGameMode(GameType.SURVIVAL);assemblies++;
            }
            if(block.kind()==ElvenDecorBlock.Kind.WALL)walls++;
            prepare(level,pos);place(level,player,block,pos,Direction.NORTH);
            source.sendSuccess(()->Component.literal("DECOR_OBJECT_PASS "+id+" four_facings=true recipe=true pure=true drops=1"),false);
        }
        final String summary="DECOR_AUDIT_PASS objects="+index+" rotations="+placements+" assemblies="+assemblies+" walls="+walls;
        source.sendSuccess(()->Component.literal(summary),false);return index;
    }
    private static int inspect(CommandSourceStack source) {
        var level=level(source);int index=0,parts=0;
        for(var entry:Leyworks.ELVEN_DECOR.entrySet()) {
            var pos=ORIGIN.offset(index%6*8,0,index/6*8);index++;var block=(ElvenDecorBlock)entry.getValue().get();var state=level.getBlockState(pos);
            require(state.is(block)&&state.getValue(ElvenDecorBlock.PART)==ElvenDecorBlock.Part.BASE&&state.getValue(ElvenDecorBlock.FACING)==Direction.NORTH,"saved decorative base "+entry.getKey());parts++;
            if(block.assembled()) {var extension=level.getBlockState(other(block,pos,Direction.NORTH));require(extension.is(block)&&extension.getValue(ElvenDecorBlock.PART)==ElvenDecorBlock.Part.EXTENSION,"saved partner");parts++;}
        }
        final String message="DECOR_RELOAD_PASS objects="+index+" parts="+parts;source.sendSuccess(()->Component.literal(message),false);return parts;
    }
}

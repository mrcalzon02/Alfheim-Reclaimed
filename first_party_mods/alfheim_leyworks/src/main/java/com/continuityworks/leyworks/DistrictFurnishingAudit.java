package com.continuityworks.leyworks;

import com.mojang.authlib.GameProfile;
import java.util.UUID;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.Container;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.*;
import net.minecraft.world.item.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.common.util.FakePlayerFactory;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraft.commands.Commands;
import net.minecraft.commands.CommandSourceStack;

/** Reproducible interaction checks. Mutating commands refuse all non-validation worlds. */
@Mod.EventBusSubscriber(modid=Leyworks.MOD_ID)
public final class DistrictFurnishingAudit {
    private static final BlockPos ORIGIN=new BlockPos(1024,192,1024);
    private DistrictFurnishingAudit() {}
    @SubscribeEvent public static void register(RegisterCommandsEvent event) {
        var root=Commands.literal("alfheimfurnish").requires(s->s.hasPermission(4));
        root.then(Commands.literal("audit").executes(c->{
            try{return audit(c.getSource());}
            catch(RuntimeException failure){
                org.slf4j.LoggerFactory.getLogger(DistrictFurnishingAudit.class).error("FURNISH_FAIL native interaction audit",failure);
                c.getSource().sendFailure(Component.literal("FURNISH_FAIL "+failure));return 0;
            }
        }));
        root.then(Commands.literal("automation").executes(c->automation(c.getSource(),false)));
        root.then(Commands.literal("persistence").executes(c->automation(c.getSource(),true)));
        event.getDispatcher().register(root);
    }
    private static void require(boolean value,String detail) {if(!value)throw new IllegalStateException("FURNISH_FAIL "+detail);}
    private static ServerLevel level(CommandSourceStack source) {
        require(source.getServer().getWorldData().getLevelName().startsWith("validation-"),"disposable validation world required");
        return source.getLevel();
    }
    private static void say(CommandSourceStack source,String message) {source.sendSuccess(()->Component.literal(message),false);}
    private static int total(Container container) {
        int total=0;for(int i=0;i<container.getContainerSize();i++)total+=container.getItem(i).getCount();return total;
    }
    private static int audit(CommandSourceStack source) {
        ServerLevel level=level(source);
        var player=FakePlayerFactory.get(level,new GameProfile(UUID.fromString("02727aa7-14ab-4e69-bad5-df882d9267d1"),"[FurnishingAudit]"));
        int index=0,storages=0,stations=0,recipes=0;
        for(var entry:Leyworks.DISTRICT_FURNISHINGS.entrySet()) {
            var block=entry.getValue().get();var id=BuiltInRegistries.BLOCK.getKey(block);
            var pos=ORIGIN.offset(index++*3,0,0);player.setPos(pos.getX()+.5,pos.getY(),pos.getZ()+.5);
            level.setBlockAndUpdate(pos,Blocks.AIR.defaultBlockState());
            BlockState state=block.defaultBlockState();level.setBlockAndUpdate(pos,state);
            var recipe=level.getRecipeManager().byKey(id).orElseThrow();
            require(recipe.getResultItem(level.registryAccess()).is(block.asItem()),"recipe output "+id);
            require(recipe.getIngredients().stream().allMatch(i->i.getItems().length>0),"recipe ingredients "+id);recipes++;
            if(block instanceof ElvenContainerBlock containerBlock) {
                var storage=(ElvenContainerBlockEntity)level.getBlockEntity(pos);require(storage!=null,"container entity "+id);
                int capacity=containerBlock.style().capacity();storage.clearContent();storage.setItem(0,new ItemStack(Items.WHEAT,16));
                player.getInventory().clearContent();player.getInventory().setItem(0,new ItemStack(Items.WHEAT_SEEDS,32));
                var menu=(MannaStoneStorageMenu)storage.createMenu(100+index,player.getInventory(),player);
                require(menu.stillValid(player)&&menu.activeSlots()==capacity,"active capacity "+id);
                require(!menu.getSlot(capacity).mayPlace(new ItemStack(Items.STONE)),"locked player insertion "+id);
                require(!storage.canPlaceItem(capacity,new ItemStack(Items.STONE)),"locked hopper insertion "+id);
                require(!menu.quickMoveStack(player,135).isEmpty(),"shift click "+id);
                require(total(storage)==48&&player.getInventory().getItem(0).isEmpty(),"shift transfer conservation "+id);
                var restored=(ElvenContainerBlockEntity)BlockEntity.loadStatic(pos,state,storage.saveWithFullMetadata());
                require(restored!=null&&restored.capacity()==capacity&&total(restored)==48,"NBT round trip "+id);
                require(containerBlock.getAnalogOutputSignal(state,level,pos)>0,"comparator "+id);
                menu.removed(player);
                // Real break recovery: onRemove drops contents, not a portable inventory nesting item.
                var area=new net.minecraft.world.phys.AABB(pos).inflate(1);
                for(var item:level.getEntitiesOfClass(net.minecraft.world.entity.item.ItemEntity.class,area))item.discard();
                level.setBlockAndUpdate(pos,Blocks.AIR.defaultBlockState());
                var drops=level.getEntitiesOfClass(net.minecraft.world.entity.item.ItemEntity.class,area);
                require(drops.stream().mapToInt(e->e.getItem().getCount()).sum()==48,"recoverable break contents "+id);
                drops.forEach(net.minecraft.world.entity.Entity::discard);
                level.setBlockAndUpdate(pos,state);storage=(ElvenContainerBlockEntity)level.getBlockEntity(pos);
                storage.setItem(0,new ItemStack(Items.WHEAT,32));
                level.setBlockAndUpdate(pos.below(),Blocks.HOPPER.defaultBlockState());
                ((Container)level.getBlockEntity(pos.below())).clearContent();
                // Stop hopper ejection; it may only pull from the cabinet during the timed test.
                level.setBlockAndUpdate(pos.below(2),Blocks.STONE.defaultBlockState());
                say(source,"FURNISH_STORAGE_PASS "+id+" slots="+capacity+" shift=32 nbt=48 dropped=48 comparator=true");storages++;
            } else if(block instanceof DistrictStationBlock station) {
                var menu=station.menu(200+index,player.getInventory(),ContainerLevelAccess.create(level,pos));
                player.containerMenu=menu;require(menu.stillValid(player),"custom station validity "+id);
                int output=0;
                switch(station.kind()) {
                    case CRAFT -> {menu.getSlot(1).set(new ItemStack(Items.OAK_LOG));output=0;}
                    case STONECUT -> {menu.getSlot(0).set(new ItemStack(Items.STONE));require(menu.clickMenuButton(player,0),"stonecut selection");output=1;}
                    case LOOM -> {menu.getSlot(0).set(new ItemStack(Items.WHITE_BANNER));menu.getSlot(1).set(new ItemStack(Items.GREEN_DYE));require(menu.clickMenuButton(player,0),"loom selection");output=3;}
                    case CARTOGRAPHY -> {menu.getSlot(0).set(MapItem.create(level,0,0,(byte)0,false,false));menu.getSlot(1).set(new ItemStack(Items.PAPER));output=2;}
                    case GRINDSTONE -> {var first=new ItemStack(Items.IRON_SWORD);first.setDamageValue(150);var second=first.copy();menu.getSlot(0).set(first);menu.getSlot(1).set(second);output=2;}
                }
                require(!menu.getSlot(output).getItem().isEmpty(),"station result "+id);
                var expected=menu.getSlot(output).getItem().copy();
                menu.clicked(output,0,ClickType.PICKUP,player);
                boolean correctOutput=ItemStack.isSameItemSameTags(menu.getCarried(),expected);
                if(station.kind()==DistrictStationBlock.Kind.CARTOGRAPHY) {
                    // Taking a scaled map creates new saved data/map ID and removes its
                    // preview scale-direction tag. Verify the resulting scale, not preview NBT.
                    var map=MapItem.getSavedData(menu.getCarried(),level);
                    correctOutput=menu.getCarried().is(Items.FILLED_MAP)&&map!=null&&map.scale==1;
                }
                require(correctOutput&&menu.getCarried().getCount()==expected.getCount(),"actual output pickup "+id);
                require(menu.getSlot(station.kind()==DistrictStationBlock.Kind.CRAFT?1:0).getItem().isEmpty(),"consumed input "+id);
                menu.setCarried(ItemStack.EMPTY);
                player.setPos(pos.getX()+20,pos.getY(),pos.getZ());require(!menu.stillValid(player),"distance closure "+id);
                player.setPos(pos.getX()+.5,pos.getY(),pos.getZ()+.5);level.setBlockAndUpdate(pos,Blocks.AIR.defaultBlockState());
                require(!menu.stillValid(player),"removed block closure "+id);menu.removed(player);player.containerMenu=player.inventoryMenu;
                level.setBlockAndUpdate(pos,state);
                say(source,"FURNISH_STATION_PASS "+id+" result="+BuiltInRegistries.ITEM.getKey(expected.getItem())+" count="+expected.getCount()+" consumed=true distance=true removal=true");stations++;
            }
        }
        say(source,"FURNISH_AUDIT_PASS storage="+storages+" stations="+stations+" recipes="+recipes);return recipes;
    }
    private static int automation(CommandSourceStack source,boolean persistence) {
        ServerLevel level=level(source);int index=0,count=0;
        for(var entry:Leyworks.DISTRICT_FURNISHINGS.entrySet()) {
            var pos=ORIGIN.offset(index++*3,0,0);if(!(entry.getValue().get() instanceof ElvenContainerBlock))continue;
            require(level.getBlockEntity(pos) instanceof ElvenContainerBlockEntity,"saved block entity "+entry.getKey());
            var storage=(ElvenContainerBlockEntity)level.getBlockEntity(pos);
            require(level.getBlockEntity(pos.below()) instanceof Container,"hopper "+entry.getKey());
            var hopper=(Container)level.getBlockEntity(pos.below());
            require(total(hopper)>0&&total(storage)+total(hopper)==32,"hopper/persistence conservation "+entry.getKey());
            say(source,"FURNISH_"+(persistence?"PERSISTENCE":"HOPPER")+"_PASS "+entry.getKey()+" cabinet="+total(storage)+" hopper="+total(hopper)+" total=32");count++;
        }
        require(count==6,"six storage fixtures");return count;
    }
}

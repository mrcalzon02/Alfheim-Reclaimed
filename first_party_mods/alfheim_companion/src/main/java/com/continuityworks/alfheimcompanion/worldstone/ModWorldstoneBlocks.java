package com.continuityworks.alfheimcompanion.worldstone;

import com.continuityworks.alfheimcompanion.AlfheimCompanion;
import com.continuityworks.alfheimcompanion.registry.ModItems;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.AmethystClusterBlock;
import net.minecraft.world.level.block.DropExperienceBlock;
import net.minecraft.util.valueproviders.UniformInt;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.minecraftforge.registries.*;

/** Natural budding Worldstone, its mineral resources and the discovery compass. */
public final class ModWorldstoneBlocks {
    public static final DeferredRegister<Block> BLOCKS=DeferredRegister.create(ForgeRegistries.BLOCKS,AlfheimCompanion.MOD_ID);
    public static final RegistryObject<Block> CRYSTAL=BLOCKS.register("worldstone_crystal",()->new WorldstoneBuddingBlock(properties(3)));
    public static final RegistryObject<Block> HEART=BLOCKS.register("worldstone_heart",()->crystal(15));
    public static final RegistryObject<Block> ORE=BLOCKS.register("worldstone_fragment_ore",()->new DropExperienceBlock(properties(4),UniformInt.of(3,7)));
    public static final RegistryObject<Block> SMALL=BLOCKS.register("worldstone_small_bud",()->bud(3,4,3));
    public static final RegistryObject<Block> MEDIUM=BLOCKS.register("worldstone_medium_bud",()->bud(4,3,6));
    public static final RegistryObject<Block> LARGE=BLOCKS.register("worldstone_large_bud",()->bud(5,3,9));
    public static final RegistryObject<Block> CLUSTER=BLOCKS.register("worldstone_cluster",()->bud(7,3,12));
    public static final RegistryObject<Item> CRYSTAL_ITEM=ModItems.REGISTRY.register("worldstone_crystal",()->new BlockItem(CRYSTAL.get(),new Item.Properties()));
    public static final RegistryObject<Item> HEART_ITEM=ModItems.REGISTRY.register("worldstone_heart",()->new BlockItem(HEART.get(),new Item.Properties()));
    public static final RegistryObject<Item> ORE_ITEM=ModItems.REGISTRY.register("worldstone_fragment_ore",()->new BlockItem(ORE.get(),new Item.Properties()));
    public static final RegistryObject<Item> CLUSTER_ITEM=ModItems.REGISTRY.register("worldstone_cluster",()->new BlockItem(CLUSTER.get(),new Item.Properties()));
    public static final RegistryObject<Item> FRAGMENT=ModItems.REGISTRY.register("worldstone_fragment",()->new WorldstoneMaterialItem(false));
    public static final RegistryObject<Item> ATTUNED=ModItems.REGISTRY.register("attuned_worldstone",()->new WorldstoneMaterialItem(true));
    public static final RegistryObject<Item> COMPASS=ModItems.REGISTRY.register("worldstone_compass",WorldstoneCompassItem::new);
    private static BlockBehaviour.Properties properties(int light) {
        return BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_RED).strength(8,1200)
            .sound(SoundType.AMETHYST).requiresCorrectToolForDrops().lightLevel(s->light);
    }
    private static Block crystal(int light) {
        return new Block(properties(light));
    }
    private static Block bud(int height,int offset,int light){return new AmethystClusterBlock(height,offset,BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_RED).strength(1.5f).noOcclusion().sound(SoundType.AMETHYST_CLUSTER).lightLevel(s->light));}
    private ModWorldstoneBlocks(){}
}

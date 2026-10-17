package com.continuityworks.alfheimcompanion.fey;

import com.continuityworks.alfheimcompanion.AlfheimCompanion;
import com.continuityworks.alfheimcompanion.registry.ModItems;
import net.minecraft.world.item.*;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraftforge.registries.*;
import java.util.*;

public final class ModFeyHomes {
    public static final String[] SEASONS={"spring","summer","autumn","winter"};
    public static final DeferredRegister<Block> BLOCKS=DeferredRegister.create(ForgeRegistries.BLOCKS,AlfheimCompanion.MOD_ID);
    public static final DeferredRegister<BlockEntityType<?>> ENTITIES=DeferredRegister.create(ForgeRegistries.BLOCK_ENTITY_TYPES,AlfheimCompanion.MOD_ID);
    public static final List<RegistryObject<FeyHomeBlock>> HOMES=new ArrayList<>();
    public static final List<RegistryObject<Item>> ITEMS=new ArrayList<>();
    static {for(String season:SEASONS){var block=BLOCKS.register(season+"_fey_apartment",()->new FeyHomeBlock(season));HOMES.add(block);ITEMS.add(ModItems.REGISTRY.register(season+"_fey_apartment",()->new BlockItem(block.get(),new Item.Properties().stacksTo(1))));}}
    public static final RegistryObject<BlockEntityType<FeyHomeBlockEntity>> HOME=ENTITIES.register("fey_home",()->BlockEntityType.Builder.of(FeyHomeBlockEntity::new,HOMES.stream().map(RegistryObject::get).toArray(Block[]::new)).build(null));
    private ModFeyHomes(){}
}

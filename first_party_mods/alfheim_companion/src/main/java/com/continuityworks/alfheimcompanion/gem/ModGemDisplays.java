package com.continuityworks.alfheimcompanion.gem;

import com.continuityworks.alfheimcompanion.AlfheimCompanion;
import com.continuityworks.alfheimcompanion.registry.ModItems;
import com.google.gson.Gson;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import net.minecraft.world.item.*;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraftforge.registries.*;

public final class ModGemDisplays {
    public record Entry(String id,String name,String item,String color,String accent){}
    public static final List<Entry> CATALOG=load();
    private static List<Entry> load(){
        try(var input=ModGemDisplays.class.getResourceAsStream("/assets/alfheim_companion/gemstone_displays.json")){
            if(input==null)throw new IllegalStateException("Missing generated gemstone display catalogue");
            return List.of(new Gson().fromJson(new InputStreamReader(input,StandardCharsets.UTF_8),Entry[].class));
        }catch(IOException e){throw new IllegalStateException(e);}
    }
    public static final DeferredRegister<Block> BLOCKS=DeferredRegister.create(ForgeRegistries.BLOCKS,AlfheimCompanion.MOD_ID);
    public static final DeferredRegister<BlockEntityType<?>> ENTITIES=DeferredRegister.create(ForgeRegistries.BLOCK_ENTITY_TYPES,AlfheimCompanion.MOD_ID);
    public static final RegistryObject<GemDisplayBlock> PEDESTAL=BLOCKS.register("geologist_pedestal",GemDisplayBlock::new);
    public static final RegistryObject<Item> EMPTY=ModItems.REGISTRY.register("geologist_pedestal",()->new BlockItem(PEDESTAL.get(),new Item.Properties()));
    public static final List<RegistryObject<Item>> FILLED=new ArrayList<>();
    static {for(var entry:CATALOG)FILLED.add(ModItems.REGISTRY.register(entry.id()+"_display_pedestal",()->new SampleItem(entry)));}
    public static final RegistryObject<BlockEntityType<GemDisplayBlockEntity>> DISPLAY=ENTITIES.register("gem_display",()->BlockEntityType.Builder.of(GemDisplayBlockEntity::new,PEDESTAL.get()).build(null));
    public static Entry find(ItemStack stack){var key=ForgeRegistries.ITEMS.getKey(stack.getItem());if(key==null)return null;return CATALOG.stream().filter(e->e.item().equals(key.toString())).findFirst().orElse(null);}
    public static final class SampleItem extends BlockItem {
        public final Entry entry;
        SampleItem(Entry entry){super(PEDESTAL.get(),new Item.Properties().stacksTo(1));this.entry=entry;}
        // Keep the empty pedestal as the canonical block item; sample selections do not overwrite it.
        @Override public void registerBlocks(Map<Block,Item> map,Item item){}
    }
    private ModGemDisplays(){}
}

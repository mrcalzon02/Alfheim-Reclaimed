package com.continuityworks.leyworks;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.minecraftforge.registries.RegistryObject;
import org.jetbrains.annotations.Nullable;

/** Real utility furniture, registered independently of world-generation placement. */
public final class DistrictFurnishings {
    private DistrictFurnishings() {}
    public static Map<String, RegistryObject<Block>> register() {
        var blocks = new LinkedHashMap<String, RegistryObject<Block>>();
        for (var style : ElvenContainerBlock.Style.values()) {
            if (!style.name().startsWith("DISTRICT_")) continue;
            String id=style.name().toLowerCase(java.util.Locale.ROOT);
            RegistryObject<Block> block=Leyworks.BLOCKS.register(id,()->new ElvenContainerBlock(properties(),style));
            blocks.put(id,block);item(id,block);
        }
        for (var kind : DistrictStationBlock.Kind.values()) {
            String id=kind.id;
            RegistryObject<Block> block=Leyworks.BLOCKS.register(id,()->new DistrictStationBlock(properties(),kind));
            blocks.put(id,block);item(id,block);
        }
        return java.util.Collections.unmodifiableMap(blocks);
    }
    private static BlockBehaviour.Properties properties() {
        return BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_BROWN).strength(2.5F,6F).noOcclusion();
    }
    private static void item(String id,RegistryObject<Block> block) {
        Leyworks.ITEMS.register(id,()->new BlockItem(block.get(),new Item.Properties()) {
            @Override public void appendHoverText(ItemStack stack,@Nullable Level level,List<Component> lines,TooltipFlag flag) {
                super.appendHoverText(stack,level,lines,flag);
                lines.add(Component.translatable("tooltip.alfheim_leyworks."+id).withStyle(net.minecraft.ChatFormatting.GRAY));
            }
        });
    }
    static Block[] containerBlocks(Block... original) {
        var blocks=new java.util.ArrayList<Block>(List.of(original));
        for (var ref:Leyworks.DISTRICT_FURNISHINGS.values())
            if(ref.get() instanceof ElvenContainerBlock) blocks.add(ref.get());
        return blocks.toArray(Block[]::new);
    }
}

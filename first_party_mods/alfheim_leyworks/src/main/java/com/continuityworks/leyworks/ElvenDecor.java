package com.continuityworks.leyworks;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.List;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.*;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.minecraftforge.registries.RegistryObject;
import org.jetbrains.annotations.Nullable;

public final class ElvenDecor {
    private ElvenDecor() {}
    static Map<String,RegistryObject<Block>> register() {
        var blocks=new LinkedHashMap<String,RegistryObject<Block>>();
        for(var def:ElvenDecorDefinitions.all()) {
            RegistryObject<Block> block=Leyworks.BLOCKS.register(def.id(),()->new ElvenDecorBlock(BlockBehaviour.Properties.of()
                .mapColor(MapColor.TERRACOTTA_WHITE).strength(1.5F,4F).noOcclusion().isValidSpawn((s,l,p,e)->false)
                .sound(def.id().contains("knight")||def.id().contains("goddess")?SoundType.STONE:SoundType.WOOD),def));
            blocks.put(def.id(),block);
            Leyworks.ITEMS.register(def.id(),()->new BlockItem(block.get(),new Item.Properties()) {
                @Override public void appendHoverText(ItemStack stack,@Nullable Level level,List<Component> lines,TooltipFlag flag) {
                    super.appendHoverText(stack,level,lines,flag);lines.add(Component.translatable("tooltip.alfheim_leyworks."+def.id()).withStyle(net.minecraft.ChatFormatting.GRAY));
                }
            });
        }
        return java.util.Collections.unmodifiableMap(blocks);
    }
}

package com.continuityworks.alfheimcompanion.gem;

import com.continuityworks.alfheimcompanion.AlfheimCompanion;
import com.continuityworks.alfheimcompanion.registry.ModItems;
import net.minecraft.network.chat.Component;
import net.minecraft.ChatFormatting;
import net.minecraft.world.item.*;
import net.minecraft.world.level.Level;
import net.minecraft.world.item.crafting.RecipeSerializer;
import net.minecraftforge.registries.*;
import java.util.*;

/** The fixed catalogue is the receipt: each consecutive inlay accounts for eight unique gems. */
public final class ModEternityCrown {
    public static final int PER_INLAY=8;
    public static final int LAYERS=ModGemDisplays.CATALOG.size()/PER_INLAY;
    public static final String PROGRESS="EternityInlays";
    public static final DeferredRegister<RecipeSerializer<?>> RECIPES=DeferredRegister.create(ForgeRegistries.RECIPE_SERIALIZERS,AlfheimCompanion.MOD_ID);
    public static final RegistryObject<RecipeSerializer<CrownSettingRecipe>> SETTING=RECIPES.register("crown_setting",CrownSettingRecipe.Serializer::new);
    public static final RegistryObject<Item> PLATINUM=plain("platinum_ingot");
    public static final RegistryObject<Item> PLATINUM_BLOCK=plain("platinum_billet");
    public static final RegistryObject<Item> CONCENTRATE=plain("platinum_concentrate");
    public static final RegistryObject<Item> SEGMENT=plain("royal_crown_segment");
    public static final RegistryObject<Item> SETTER=ModItems.REGISTRY.register("eternity_setter",()->new Item(new Item.Properties().stacksTo(1)){
        @Override public boolean hasCraftingRemainingItem(ItemStack stack){return true;}
        @Override public ItemStack getCraftingRemainingItem(ItemStack stack){var copy=stack.copy();copy.setCount(1);return copy;}
        @Override public void appendHoverText(ItemStack stack,Level level,List<Component> text,TooltipFlag flag){
            text.add(Component.literal("Sets an inlay into a crown in a crafting grid.").withStyle(ChatFormatting.GRAY));
            text.add(Component.literal("Reusable; returned after each setting.").withStyle(ChatFormatting.GOLD));
        }
    });
    public static final RegistryObject<Item> BASE=ModItems.REGISTRY.register("gold_platinum_crown",()->new EternityCrownItem(false));
    public static final RegistryObject<Item> COMPLETE=ModItems.REGISTRY.register("crown_of_eternity",()->new EternityCrownItem(true));
    public static final List<RegistryObject<Item>> INLAYS=new ArrayList<>();
    static {
        if(ModGemDisplays.CATALOG.size()!=232||LAYERS*PER_INLAY!=232)throw new IllegalStateException("Crown catalogue requires a deliberate migration when changed");
        for(int index=0;index<LAYERS;index++){
            final int layer=index;
            INLAYS.add(ModItems.REGISTRY.register(String.format(Locale.ROOT,"eternity_inlay_%02d",index+1),()->new Item(new Item.Properties()){
                @Override public void appendHoverText(ItemStack stack,Level level,List<Component> text,TooltipFlag flag){
                    text.add(Component.literal("Inlay "+(layer+1)+" of "+LAYERS+" • eight unique gems").withStyle(ChatFormatting.GOLD));
                    for(int i=layer*PER_INLAY;i<(layer+1)*PER_INLAY;i++)text.add(Component.literal(ModGemDisplays.CATALOG.get(i).name()).withStyle(ChatFormatting.GRAY));
                }
            }));
        }
    }
    private static RegistryObject<Item> plain(String id){return ModItems.REGISTRY.register(id,()->new Item(new Item.Properties()));}
    public static int progress(ItemStack stack){return stack.is(COMPLETE.get())?LAYERS:stack.hasTag()?stack.getTag().getInt(PROGRESS):0;}
    public static ItemStack preview(int layers){
        var stack=new ItemStack(layers==LAYERS?COMPLETE.get():BASE.get());
        if(layers>0)stack.getOrCreateTag().putInt(PROGRESS,layers);
        return stack;
    }
    private ModEternityCrown(){}
}

package com.continuityworks.alfheimcompanion.gem;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.item.*;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.level.Level;
import java.util.List;

/** Wearable regalia, without combat attributes or durability loss. */
public final class EternityCrownItem extends ArmorItem {
    private static final ArmorMaterial MATERIAL=new ArmorMaterial(){
        public int getDurabilityForType(ArmorItem.Type type){return 0;}
        public int getDefenseForType(ArmorItem.Type type){return 0;}
        public int getEnchantmentValue(){return 0;}
        public SoundEvent getEquipSound(){return SoundEvents.ARMOR_EQUIP_GOLD;}
        public Ingredient getRepairIngredient(){return Ingredient.EMPTY;}
        public String getName(){return "alfheim_companion:eternity_crown";}
        public float getToughness(){return 0;}
        public float getKnockbackResistance(){return 0;}
    };
    private final boolean complete;
    public EternityCrownItem(boolean complete){super(MATERIAL,ArmorItem.Type.HELMET,new Item.Properties().stacksTo(1).rarity(complete?Rarity.EPIC:Rarity.RARE));this.complete=complete;}
    @Override public boolean isFoil(ItemStack stack){return complete;}
    @Override public void appendHoverText(ItemStack stack,Level level,List<Component> text,TooltipFlag flag){
        int set=ModEternityCrown.progress(stack);
        text.add(Component.literal((set*8)+" / 232 gemstones inset • "+set+" / 29 inlays").withStyle(ChatFormatting.GOLD));
        if(complete){text.add(Component.literal("One of every gemstone, held beyond time.").withStyle(ChatFormatting.LIGHT_PURPLE));return;}
        if(set<0||set>=ModEternityCrown.LAYERS)return;
        text.add(Component.literal("Next: Eternity Inlay "+(set+1)+" + Jeweller's Eternity Setter").withStyle(ChatFormatting.AQUA));
        for(int i=set*8;i<(set+1)*8;i++)text.add(Component.literal("  "+ModGemDisplays.CATALOG.get(i).name()).withStyle(ChatFormatting.GRAY));
    }
    @Override public String getArmorTexture(ItemStack stack,Entity entity,EquipmentSlot slot,String type){return "alfheim_companion:textures/models/armor/eternity_crown.png";}
    @Override public void initializeClient(java.util.function.Consumer<net.minecraftforge.client.extensions.common.IClientItemExtensions> consumer){
        consumer.accept(new com.continuityworks.alfheimcompanion.client.EternityCrownAppearance());
    }
}

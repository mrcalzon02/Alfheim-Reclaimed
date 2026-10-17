package com.continuityworks.alfheimcompanion.gem;

import com.google.gson.JsonObject;
import net.minecraft.core.RegistryAccess;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.GsonHelper;
import net.minecraft.world.inventory.CraftingContainer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.*;
import net.minecraft.world.level.Level;

/** Shapeless recipe with a strict saved stage; recipe-book output also carries the correct stage. */
public final class CrownSettingRecipe extends ShapelessRecipe {
    private final int required;
    public CrownSettingRecipe(ShapelessRecipe base,int required){
        super(base.getId(),base.getGroup(),CraftingBookCategory.EQUIPMENT,ModEternityCrown.preview(required+1),base.getIngredients());
        if(required<0||required>=ModEternityCrown.LAYERS)throw new IllegalArgumentException("Invalid crown stage");
        this.required=required;
    }
    @Override public boolean matches(CraftingContainer grid,Level level){
        if(!super.matches(grid,level))return false;
        for(int i=0;i<grid.getContainerSize();i++)if(grid.getItem(i).is(ModEternityCrown.BASE.get()))return ModEternityCrown.progress(grid.getItem(i))==required;
        return false;
    }
    @Override public ItemStack assemble(CraftingContainer grid,RegistryAccess access){
        for(int i=0;i<grid.getContainerSize();i++){
            var old=grid.getItem(i);
            if(old.is(ModEternityCrown.BASE.get())&&ModEternityCrown.progress(old)==required){
                var result=ModEternityCrown.preview(required+1);
                if(old.hasTag())result.setTag(old.getTag().copy());
                result.getOrCreateTag().putInt(ModEternityCrown.PROGRESS,required+1);
                return result;
            }
        }
        return ItemStack.EMPTY;
    }
    @Override public RecipeSerializer<?> getSerializer(){return ModEternityCrown.SETTING.get();}
    public static final class Serializer implements RecipeSerializer<CrownSettingRecipe>{
        private final ShapelessRecipe.Serializer delegate=new ShapelessRecipe.Serializer();
        @Override public CrownSettingRecipe fromJson(ResourceLocation id,JsonObject json){return new CrownSettingRecipe(delegate.fromJson(id,json),GsonHelper.getAsInt(json,"required_inlays"));}
        @Override public CrownSettingRecipe fromNetwork(ResourceLocation id,FriendlyByteBuf buffer){int stage=buffer.readVarInt();return new CrownSettingRecipe(delegate.fromNetwork(id,buffer),stage);}
        @Override public void toNetwork(FriendlyByteBuf buffer,CrownSettingRecipe recipe){buffer.writeVarInt(recipe.required);delegate.toNetwork(buffer,recipe);}
    }
}

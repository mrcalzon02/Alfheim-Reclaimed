package com.continuityworks.alfheimcompanion.worldstone;

import com.continuityworks.alfheimcompanion.worldgen.WorldstoneNavigation;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.item.*;
import net.minecraft.world.level.Level;
import java.util.List;

public final class WorldstoneCompassItem extends CompassItem {
    public WorldstoneCompassItem(){super(new Item.Properties().stacksTo(1));}
    @Override public String getDescriptionId(ItemStack stack){return "item.alfheim_companion.worldstone_compass";}
    @Override public void inventoryTick(ItemStack stack,Level level,Entity holder,int slot,boolean selected) {
        super.inventoryTick(stack,level,holder,slot,selected);
        if(!level.isClientSide && holder instanceof ServerPlayer player && stack.getOrCreateTag().getBoolean("WorldstoneSeeking")
            && !WorldstoneNavigation.isSeeking(player.getUUID(),stack))stack.getOrCreateTag().putBoolean("WorldstoneSeeking",false);
    }
    @Override public InteractionResultHolder<ItemStack> use(Level level,Player player,InteractionHand hand) {
        var stack=player.getItemInHand(hand);
        if(player instanceof ServerPlayer serverPlayer) {
            if(!level.dimension().location().toString().equals("mythicbotany:alfheim")) {
                player.displayClientMessage(Component.literal("The Worldstone's call can only be heard in Alfheim."),true);
                return InteractionResultHolder.fail(stack);
            }
            if(isLodestoneCompass(stack) && !player.isShiftKeyDown()) {
                var target=getLodestonePosition(stack.getOrCreateTag());
                if(target!=null)player.displayClientMessage(Component.literal("Worldstone: "+target.pos().getX()+", "+target.pos().getZ()+" in Alfheim."),true);
            } else WorldstoneNavigation.begin(serverPlayer,stack);
            player.getCooldowns().addCooldown(this,20);
        }
        return InteractionResultHolder.sidedSuccess(stack,level.isClientSide);
    }
    @Override public void appendHoverText(ItemStack stack,Level level,List<Component> lines,TooltipFlag flag) {
        lines.add(Component.literal("Right-click to seek a Worldstone in Alfheim."));
        lines.add(Component.literal("Sneak and right-click to seek again."));
        var target=getLodestonePosition(stack.getOrCreateTag());
        if(target!=null)lines.add(Component.literal("Worldstone: "+target.pos().getX()+", "+target.pos().getZ()));
        if(stack.getOrCreateTag().getBoolean("WorldstoneSeeking"))lines.add(Component.literal("Listening for the Worldstone..."));
    }
}

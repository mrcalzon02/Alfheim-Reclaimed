package com.continuityworks.alfheimcompanion.item;

import com.continuityworks.alfheimcompanion.service.CompanionSummonService;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.UseAnim;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.TooltipFlag;
import java.util.List;

public final class CompanionSigilItem extends Item {
    public CompanionSigilItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        player.startUsingItem(hand);
        return InteractionResultHolder.consume(stack);
    }

    @Override
    public int getUseDuration(ItemStack stack) { return 72000; }

    @Override
    public UseAnim getUseAnimation(ItemStack stack) { return UseAnim.NONE; }

    @Override
    public void onUseTick(Level level, LivingEntity living, ItemStack stack, int remainingUseDuration) {
        if (level.isClientSide && getUseDuration(stack) - remainingUseDuration == 8) {
            DistExecutor.unsafeRunWhenOn(Dist.CLIENT, () -> () ->
                    com.continuityworks.alfheimcompanion.client.ClientWheelHooks.open());
        }
    }

    @Override
    public void releaseUsing(ItemStack stack, Level level, LivingEntity living, int timeLeft) {
        int heldTicks = getUseDuration(stack) - timeLeft;
        if (!level.isClientSide && heldTicks < 8 && living instanceof ServerPlayer player) {
            if (player.isShiftKeyDown()) CompanionSummonService.dismiss(player);
            else CompanionSummonService.summonOrRecall(player);
            player.getCooldowns().addCooldown(this, 20);
        }
    }

    @Override
    public void appendHoverText(ItemStack stack, Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.literal("Quick use: summon or recall"));
        tooltip.add(Component.literal("Hold: open command wheel (also bound to V)"));
        tooltip.add(Component.literal("Crouch + quick use: dismiss"));
    }
}

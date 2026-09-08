package com.continuityworks.alfheimcompanion.item;

import com.continuityworks.alfheimcompanion.service.CompanionSummonService;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

public final class CompanionSigilItem extends Item {
    public CompanionSigilItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (level.isClientSide || !(player instanceof ServerPlayer serverPlayer)) {
            return InteractionResultHolder.sidedSuccess(stack, level.isClientSide);
        }

        if (player.isShiftKeyDown()) {
            CompanionSummonService.dismiss(serverPlayer);
        } else {
            CompanionSummonService.summonOrRecall(serverPlayer);
        }
        player.getCooldowns().addCooldown(this, 20);
        return InteractionResultHolder.consume(stack);
    }
}

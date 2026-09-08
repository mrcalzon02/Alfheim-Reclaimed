package com.continuityworks.alfheimcompanion.service;

import com.continuityworks.alfheimcompanion.entity.ElvenCompanionEntity;
import com.continuityworks.alfheimcompanion.integration.ClaimPermissionBridge;
import com.mojang.authlib.GameProfile;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraftforge.common.util.FakePlayer;
import net.minecraftforge.common.util.FakePlayerFactory;

import java.nio.charset.StandardCharsets;
import java.util.UUID;

/** Executes validated actions through vanilla/Forge player paths so protection mods see them. */
public final class PlayerLikeActionService {
    private PlayerLikeActionService() {}

    public static boolean breakBlock(ElvenCompanionEntity companion, ServerPlayer owner, BlockPos position) {
        if (!(companion.level() instanceof ServerLevel level)
                || !withinReach(companion, position)
                || !ClaimPermissionBridge.mayAct(owner, level, position, ClaimPermissionBridge.Action.BREAK)) {
            return false;
        }
        return fakePlayer(companion, level).gameMode.destroyBlock(position);
    }

    public static InteractionResult placeBlock(ElvenCompanionEntity companion, ServerPlayer owner,
                                                BlockPos position, BlockHitResult hit, ItemStack suppliedStack) {
        if (!(companion.level() instanceof ServerLevel level)
                || !(suppliedStack.getItem() instanceof BlockItem)
                || !withinReach(companion, position)
                || !ClaimPermissionBridge.mayAct(owner, level, position, ClaimPermissionBridge.Action.PLACE)) {
            return InteractionResult.FAIL;
        }
        FakePlayer actor = fakePlayer(companion, level);
        actor.setItemInHand(InteractionHand.MAIN_HAND, suppliedStack);
        InteractionResult result = suppliedStack.useOn(new UseOnContext(actor, InteractionHand.MAIN_HAND, hit));
        actor.setItemInHand(InteractionHand.MAIN_HAND, ItemStack.EMPTY);
        return result;
    }

    /** The only sanctioned creation path. Survival requests always fail. */
    public static boolean grantCreativeOnly(ServerPlayer requester, ElvenCompanionEntity companion, ItemStack stack) {
        if (!requester.isCreative() || stack.isEmpty()) return false;
        return companion.inventory().addItem(stack.copy()).isEmpty();
    }

    private static FakePlayer fakePlayer(ElvenCompanionEntity companion, ServerLevel level) {
        UUID id = UUID.nameUUIDFromBytes(("alfheim-companion:" + companion.getUUID())
                .getBytes(StandardCharsets.UTF_8));
        return FakePlayerFactory.get(level, new GameProfile(id, "[AlfheimCompanion]"));
    }

    private static boolean withinReach(ElvenCompanionEntity companion, BlockPos position) {
        return companion.distanceToSqr(position.getX() + 0.5D, position.getY() + 0.5D,
                position.getZ() + 0.5D) <= 36.0D;
    }
}

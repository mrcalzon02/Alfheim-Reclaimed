package com.continuityworks.alfheimcompanion.entity;

import com.continuityworks.alfheimcompanion.integration.ClaimPermissionBridge;
import com.continuityworks.alfheimcompanion.memory.CompanionMode;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.ItemStack;

import java.util.EnumSet;

final class ItemTaskGoal extends Goal {
    private final ElvenCompanionEntity companion;

    ItemTaskGoal(ElvenCompanionEntity companion) {
        this.companion = companion;
        setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    @Override
    public boolean canUse() {
        return companion.itemTaskTarget() != null && companion.level() instanceof ServerLevel;
    }

    @Override
    public boolean canContinueToUse() {
        return companion.itemTaskTarget() != null;
    }

    @Override
    public void tick() {
        if (!(companion.level() instanceof ServerLevel level)) return;
        Entity target = level.getEntity(companion.itemTaskTarget());
        if (!(target instanceof ItemEntity item) || !item.isAlive()) {
            companion.clearItemTask();
            return;
        }
        companion.getLookControl().setLookAt(item, 20.0F, companion.getMaxHeadXRot());
        if (companion.distanceToSqr(item) > 4.0D) {
            companion.getNavigation().moveTo(item, 1.15D);
            return;
        }
        if (!companion.itemTaskFetch()) {
            companion.setMode(CompanionMode.WAITING);
            companion.clearItemTask();
            return;
        }
        ServerPlayer owner = companion.resolveOwner();
        if (owner == null || !ClaimPermissionBridge.mayAct(owner, level, item.blockPosition(),
                ClaimPermissionBridge.Action.CONTAINER_EXTRACT)) {
            companion.clearItemTask();
            return;
        }
        int amount = Math.min(companion.itemTaskCount(), item.getItem().getCount());
        ItemStack taken = item.getItem().copyWithCount(amount);
        ItemStack remainder = companion.inventory().addItem(taken);
        int inserted = amount - remainder.getCount();
        if (inserted > 0) {
            item.getItem().shrink(inserted);
            if (item.getItem().isEmpty()) item.discard();
            companion.markDeliveryPending(taken, inserted);
            companion.setMode(CompanionMode.FOLLOWING);
        }
        companion.clearItemTask();
    }
}

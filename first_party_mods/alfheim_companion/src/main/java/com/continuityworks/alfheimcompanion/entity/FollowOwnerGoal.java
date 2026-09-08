package com.continuityworks.alfheimcompanion.entity;

import com.continuityworks.alfheimcompanion.memory.CompanionMode;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.ai.goal.Goal;

import java.util.EnumSet;

final class FollowOwnerGoal extends Goal {
    private final ElvenCompanionEntity companion;
    private ServerPlayer owner;

    FollowOwnerGoal(ElvenCompanionEntity companion) {
        this.companion = companion;
        setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    @Override
    public boolean canUse() {
        owner = companion.resolveOwner();
        return owner != null && companion.mode() == CompanionMode.FOLLOWING
                && companion.distanceToSqr(owner) > 16.0D;
    }

    @Override
    public boolean canContinueToUse() {
        return owner != null && owner.isAlive() && companion.mode() == CompanionMode.FOLLOWING
                && companion.distanceToSqr(owner) > 6.25D;
    }

    @Override
    public void tick() {
        companion.getLookControl().setLookAt(owner, 10.0F, companion.getMaxHeadXRot());
        if (companion.distanceToSqr(owner) > 1024.0D) {
            companion.teleportNear(owner);
        } else {
            companion.getNavigation().moveTo(owner, 1.15D);
        }
    }

    @Override
    public void stop() {
        owner = null;
        companion.getNavigation().stop();
    }
}

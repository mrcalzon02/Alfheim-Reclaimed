package com.continuityworks.alfheimcompanion.entity;

import com.continuityworks.alfheimcompanion.memory.CompanionMode;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.ai.goal.Goal;

import java.util.EnumSet;

final class GuardPositionGoal extends Goal {
    private final ElvenCompanionEntity companion;

    GuardPositionGoal(ElvenCompanionEntity companion) {
        this.companion = companion;
        setFlags(EnumSet.of(Flag.MOVE));
    }

    @Override
    public boolean canUse() {
        BlockPos anchor = companion.guardPosition();
        return companion.mode() == CompanionMode.GUARDING && anchor != null
                && companion.distanceToSqr(anchor.getX() + 0.5D, anchor.getY(), anchor.getZ() + 0.5D) > 9.0D;
    }

    @Override
    public boolean canContinueToUse() {
        return companion.mode() == CompanionMode.GUARDING && !companion.getNavigation().isDone();
    }

    @Override
    public void start() {
        BlockPos anchor = companion.guardPosition();
        if (anchor != null) companion.getNavigation().moveTo(anchor.getX() + 0.5D, anchor.getY(), anchor.getZ() + 0.5D, 1.1D);
    }
}

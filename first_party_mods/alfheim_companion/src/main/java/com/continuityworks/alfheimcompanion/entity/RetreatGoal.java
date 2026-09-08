package com.continuityworks.alfheimcompanion.entity;

import com.continuityworks.alfheimcompanion.memory.CompanionMode;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.util.DefaultRandomPos;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.phys.Vec3;

import java.util.Comparator;
import java.util.EnumSet;

final class RetreatGoal extends Goal {
    private final ElvenCompanionEntity companion;
    private Vec3 destination;

    RetreatGoal(ElvenCompanionEntity companion) {
        this.companion = companion;
        setFlags(EnumSet.of(Flag.MOVE));
    }

    @Override
    public boolean canUse() {
        if (companion.mode() != CompanionMode.RETREATING) return false;
        Monster threat = companion.level().getEntitiesOfClass(Monster.class,
                        companion.getBoundingBox().inflate(12), Monster::isAlive).stream()
                .min(Comparator.comparingDouble(companion::distanceToSqr)).orElse(null);
        destination = threat == null
                ? (companion.resolveOwner() == null ? null : companion.resolveOwner().position())
                : DefaultRandomPos.getPosAway(companion, 12, 7, threat.position());
        return destination != null;
    }

    @Override public void start() { companion.getNavigation().moveTo(destination.x, destination.y, destination.z, 1.25); }
    @Override public boolean canContinueToUse() { return companion.mode() == CompanionMode.RETREATING && !companion.getNavigation().isDone(); }
}

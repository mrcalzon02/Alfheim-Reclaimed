package com.continuityworks.alfheimcompanion.entity;

import com.continuityworks.alfheimcompanion.memory.CompanionMode;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.target.TargetGoal;
import net.minecraft.world.entity.monster.Monster;

import java.util.Comparator;

final class DefendLesseeTargetGoal extends TargetGoal {
    private final ElvenCompanionEntity companion;
    private LivingEntity candidate;

    DefendLesseeTargetGoal(ElvenCompanionEntity companion) {
        super(companion, false);
        this.companion = companion;
    }

    @Override
    public boolean canUse() {
        ServerPlayer owner = companion.resolveOwner();
        if (owner == null || owner.level() != companion.level()) return false;
        LivingEntity attacker = owner.getLastHurtByMob();
        if (attacker != null && attacker.isAlive() && companion.distanceToSqr(attacker) <= 1024.0D) {
            candidate = attacker;
            return true;
        }
        if (companion.mode() != CompanionMode.DEFENDING && companion.mode() != CompanionMode.GUARDING) return false;
        candidate = companion.level().getEntitiesOfClass(Monster.class,
                        companion.getBoundingBox().inflate(companion.mode() == CompanionMode.GUARDING ? 10 : 16),
                        LivingEntity::isAlive).stream()
                .min(Comparator.comparingDouble(companion::distanceToSqr)).orElse(null);
        return candidate != null;
    }

    @Override
    public void start() {
        companion.setTarget(candidate);
        super.start();
    }

    @Override
    public boolean canContinueToUse() {
        LivingEntity target = companion.getTarget();
        return target != null && target.isAlive()
                && (companion.mode() == CompanionMode.DEFENDING || companion.mode() == CompanionMode.GUARDING);
    }
}

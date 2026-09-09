package com.continuityworks.alfheimcompanion.service;

import com.continuityworks.alfheimcompanion.entity.ElvenCompanionEntity;
import com.continuityworks.alfheimcompanion.integration.ClaimPermissionBridge;
import com.continuityworks.alfheimcompanion.integration.ContinuityWorksBridge;
import com.continuityworks.alfheimcompanion.memory.ActiveTask;
import com.continuityworks.alfheimcompanion.memory.BaseObjective;
import com.continuityworks.alfheimcompanion.memory.BlueprintLedger;
import com.continuityworks.alfheimcompanion.memory.CompanionMode;
import com.continuityworks.alfheimcompanion.memory.CompanionSavedData;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.levelgen.Heightmap;

/** Deterministic state machine for an explicitly requested, owner-approved base of operations. */
public final class BaseOperationsService {
    private static final String SHELL_PREFIX = "companion base shell: ";
    private static final String FURNISHING_PREFIX = "companion base furnishing: ";

    private BaseOperationsService() {}

    public static void begin(ServerPlayer owner, ElvenCompanionEntity companion, String purpose) {
        CompanionSavedData data = CompanionSavedData.get(owner.server);
        if (ContinuityWorksBridge.provider().isEmpty()) {
            reply(owner, data, "I can survey a base site once the Continuity Works blueprint provider is connected.");
            return;
        }
        if (data.blueprintLedger().active()) {
            reply(owner, data, "A blueprint is already active. Finish or cancel it before starting a base objective.");
            return;
        }
        String dimension = owner.level().dimension().location().toString();
        BlockPos candidate = owner.blockPosition().relative(owner.getDirection(), 6);
        long now = owner.level().getGameTime();
        BaseObjective objective = new BaseObjective(BaseObjective.Phase.SURVEY, dimension,
                candidate, purpose == null || purpose.isBlank() ? "base of operations" : purpose, now, now);
        data.setBaseObjective(objective);
        data.setTask(baseTask(objective, now), null);
        companion.setMode(CompanionMode.WORKING);
        reply(owner, data, "I will survey this area first. Any shell and furnishing plan will be shown for approval before I alter a block.");
    }

    public static void tick(MinecraftServer server) {
        if (server.getTickCount() % 20 != 0) return;
        CompanionSavedData data = CompanionSavedData.get(server);
        BaseObjective objective = data.baseObjective();
        if (!objective.active()) return;
        ElvenCompanionEntity companion = CompanionSummonService.findLoaded(server,
                data.companionUuid().orElse(null));
        if (companion == null || !companion.isAlive()) return;
        ServerPlayer owner = companion.resolveOwner();
        if (owner == null || owner.level() != companion.level()
                || !(owner.level() instanceof ServerLevel level)) return;
        if (data.task().kind() != ActiveTask.Kind.BASE)
            data.setTask(baseTask(objective, level.getGameTime()), data.activeBlueprintId().orElse(null));

        switch (objective.phase()) {
            case SURVEY -> survey(owner, companion, level, data, objective);
            case FURNISHING -> requestFurnishing(owner, companion, data, objective);
            case PROPOSING, AWAITING_APPROVAL, BUILDING -> synchronizeLedger(data, objective,
                    level.getGameTime());
            default -> { }
        }
    }

    public static void onBlueprintPreview(CompanionSavedData data, long gameTime) {
        BaseObjective objective = data.baseObjective();
        if (!objective.active()) return;
        update(data, objective.advance(BaseObjective.Phase.AWAITING_APPROVAL, gameTime));
    }

    public static void onBlueprintApproved(CompanionSavedData data, String purpose, long gameTime) {
        BaseObjective objective = data.baseObjective();
        if (!objective.active()) return;
        BaseObjective.Phase phase = purpose != null && purpose.startsWith(FURNISHING_PREFIX)
                ? BaseObjective.Phase.FURNISHING : BaseObjective.Phase.BUILDING;
        update(data, objective.advance(phase, gameTime));
    }

    public static void onBlueprintComplete(CompanionSavedData data, ServerPlayer owner, String purpose,
                                           long gameTime) {
        BaseObjective objective = data.baseObjective();
        if (objective.phase() == BaseObjective.Phase.NONE) return;
        if (purpose != null && purpose.startsWith(FURNISHING_PREFIX)) {
            BaseObjective completed = objective.advance(BaseObjective.Phase.MAINTAINING, gameTime);
            data.setBaseObjective(completed);
            data.setTask(ActiveTask.NONE, data.activeBlueprintId().orElse(null));
            data.rememberFact("base:anchor", completed.dimensionId() + "@" + completed.anchor().asLong());
            reply(owner, data, "The base is established. I will treat it as my operating anchor and maintain it through approved work only.");
        } else {
            update(data, objective.advance(BaseObjective.Phase.FURNISHING, gameTime));
            reply(owner, data, "The shell is complete. I will prepare a separate functional furnishing proposal for approval.");
        }
    }

    public static void onBlueprintInterrupted(CompanionSavedData data, long gameTime) {
        BaseObjective objective = data.baseObjective();
        if (objective.active()) update(data, objective.advance(BaseObjective.Phase.PAUSED, gameTime));
    }

    public static void cancelObjective(MinecraftServer server) {
        CompanionSavedData data = CompanionSavedData.get(server);
        if (data.baseObjective().active()) data.setBaseObjective(BaseObjective.NONE);
    }

    private static void survey(ServerPlayer owner, ElvenCompanionEntity companion, ServerLevel level,
                               CompanionSavedData data, BaseObjective objective) {
        if (!level.dimension().location().toString().equals(objective.dimensionId())) {
            pause(owner, data, objective, "The proposed base site is in another dimension");
            return;
        }
        BlockPos anchor = grounded(level, objective.anchor());
        int minimum = Integer.MAX_VALUE;
        int maximum = Integer.MIN_VALUE;
        for (int dx = -4; dx <= 4; dx += 2) {
            for (int dz = -4; dz <= 4; dz += 2) {
                BlockPos sample = grounded(level, anchor.offset(dx, 0, dz));
                if (!level.hasChunkAt(sample)) return;
                if (!ClaimPermissionBridge.mayAct(owner, level, sample, ClaimPermissionBridge.Action.PLACE)) {
                    pause(owner, data, objective, "The candidate overlaps protected land");
                    return;
                }
                if (!level.getFluidState(sample).isEmpty() || !level.getFluidState(sample.below()).isEmpty()) {
                    pause(owner, data, objective, "The candidate is too wet for a safe foundation");
                    return;
                }
                minimum = Math.min(minimum, sample.getY());
                maximum = Math.max(maximum, sample.getY());
            }
        }
        if (maximum - minimum > 4) {
            pause(owner, data, objective, "The candidate is too steep for the bounded base footprint");
            return;
        }
        BaseObjective ready = new BaseObjective(BaseObjective.Phase.PROPOSING, objective.dimensionId(),
                anchor, objective.purpose(), objective.createdGameTime(), level.getGameTime());
        update(data, ready);
        BlueprintLifecycleService.requestAt(owner, companion, SHELL_PREFIX + objective.purpose(), anchor);
    }

    private static void requestFurnishing(ServerPlayer owner, ElvenCompanionEntity companion,
                                          CompanionSavedData data, BaseObjective objective) {
        if (data.blueprintLedger().active()) return;
        BlueprintLifecycleService.requestAt(owner, companion, FURNISHING_PREFIX + objective.purpose(),
                objective.anchor());
        update(data, objective.advance(BaseObjective.Phase.PROPOSING, owner.level().getGameTime()));
    }

    private static void synchronizeLedger(CompanionSavedData data, BaseObjective objective, long gameTime) {
        BlueprintLedger.State state = data.blueprintLedger().state();
        if (state == BlueprintLedger.State.PREVIEW && objective.phase() != BaseObjective.Phase.AWAITING_APPROVAL)
            update(data, objective.advance(BaseObjective.Phase.AWAITING_APPROVAL, gameTime));
        else if (state == BlueprintLedger.State.EXECUTING && objective.phase() != BaseObjective.Phase.BUILDING)
            update(data, objective.advance(BaseObjective.Phase.BUILDING, gameTime));
        else if (state == BlueprintLedger.State.PAUSED || state == BlueprintLedger.State.FAILED
                || state == BlueprintLedger.State.REJECTED)
            update(data, objective.advance(BaseObjective.Phase.PAUSED, gameTime));
    }

    private static BlockPos grounded(ServerLevel level, BlockPos position) {
        int y = level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, position.getX(), position.getZ());
        return new BlockPos(position.getX(), y, position.getZ());
    }

    private static void pause(ServerPlayer owner, CompanionSavedData data, BaseObjective objective, String reason) {
        update(data, objective.advance(BaseObjective.Phase.PAUSED, owner.level().getGameTime()));
        reply(owner, data, reason + ". Move to another site and ask me to establish a base again.");
    }

    private static void update(CompanionSavedData data, BaseObjective objective) {
        data.setBaseObjective(objective);
        data.setTask(baseTask(objective, objective.updatedGameTime()), data.activeBlueprintId().orElse(null));
    }

    private static ActiveTask baseTask(BaseObjective objective, long gameTime) {
        return new ActiveTask(ActiveTask.Kind.BASE, objective.phase().name(), objective.purpose(), 1, gameTime);
    }

    private static void reply(ServerPlayer owner, CompanionSavedData data, String message) {
        owner.sendSystemMessage(Component.literal("§d[" + data.companionName() + "] §f" + message));
    }
}

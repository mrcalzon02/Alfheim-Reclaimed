package com.continuityworks.alfheimcompanion.service;

import com.continuityworks.alfheimcompanion.brain.AutonomousActivityCatalog;
import com.continuityworks.alfheimcompanion.brain.AutonomousActivityDecision;
import com.continuityworks.alfheimcompanion.brain.AutonomousActivityKind;
import com.continuityworks.alfheimcompanion.brain.AutonomousActivityOption;
import com.continuityworks.alfheimcompanion.brain.AutonomousActivitySnapshot;
import com.continuityworks.alfheimcompanion.brain.CompanionBrainCoordinator;
import com.continuityworks.alfheimcompanion.entity.ElvenCompanionEntity;
import com.continuityworks.alfheimcompanion.integration.ClaimPermissionBridge;
import com.continuityworks.alfheimcompanion.memory.AutonomousActivityPlan;
import com.continuityworks.alfheimcompanion.memory.BaseObjective;
import com.continuityworks.alfheimcompanion.memory.CompanionMode;
import com.continuityworks.alfheimcompanion.memory.CompanionSavedData;
import com.continuityworks.alfheimcompanion.memory.DelegatedClaim;
import com.continuityworks.alfheimcompanion.memory.MemoryEntry;
import com.continuityworks.alfheimcompanion.memory.ObservedChunk;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.levelgen.Heightmap;

import java.util.Comparator;
import java.util.List;

/**
 * Slow single-player autonomy loop. This first executor is read-only: it may navigate and observe,
 * but never changes a block, item, claim, recipe, or blueprint.
 */
public final class AutonomousActivityService {
    private static final int TICK_INTERVAL = 20;
    private static final int REQUEST_INTERVAL = 200;
    private static final long PLAN_COOLDOWN_TICKS = 1200L;
    private static final long DECISION_TIMEOUT_TICKS = 400L;
    private static final long ACTIVITY_TIMEOUT_TICKS = 2400L;
    private static boolean decisionPending;
    private static long decisionRequestedGameTime;

    private AutonomousActivityService() {}

    public static void tick(MinecraftServer server) {
        if (server.getTickCount() % TICK_INTERVAL != 0) return;
        CompanionSavedData data = CompanionSavedData.get(server);
        ElvenCompanionEntity companion = CompanionSummonService.findLoaded(server,
                data.companionUuid().orElse(null));
        if (companion == null || !companion.isAlive() || !(companion.level() instanceof ServerLevel level)) return;
        ServerPlayer owner = companion.resolveOwner();
        if (owner == null) {
            pause(companion, data, level.getGameTime(), "owner unavailable");
            return;
        }

        long now = level.getGameTime();
        if (decisionPending && now - decisionRequestedGameTime > DECISION_TIMEOUT_TICKS)
            decisionPending = false;
        if (!eligible(server, level, owner, companion, data)) {
            pause(companion, data, now, "higher-priority state");
            return;
        }
        if (hasThreat(companion)) {
            pause(companion, data, now, "nearby threat");
            return;
        }

        AutonomousActivityPlan plan = data.autonomousActivity();
        if (plan.active()) {
            execute(level, owner, companion, data, plan);
            return;
        }
        if (decisionPending || server.getTickCount() % REQUEST_INTERVAL != 0
                || now - plan.updatedGameTime() < PLAN_COOLDOWN_TICKS) return;
        requestChoice(level, owner, companion, data);
    }

    public static void applyDecision(MinecraftServer server, AutonomousActivitySnapshot snapshot,
                                     AutonomousActivityDecision decision) {
        decisionPending = false;
        decisionRequestedGameTime = 0;
        CompanionSavedData data = CompanionSavedData.get(server);
        ElvenCompanionEntity companion = CompanionSummonService.findLoaded(server,
                data.companionUuid().orElse(null));
        if (companion == null || !(companion.level() instanceof ServerLevel level)) return;
        ServerPlayer owner = companion.resolveOwner();
        if (owner == null || !owner.getUUID().equals(snapshot.ownerUuid())
                || !eligible(server, level, owner, companion, data) || hasThreat(companion)) return;

        List<AutonomousActivityOption> current = options(data, companion, owner);
        AutonomousActivityOption selected;
        try { selected = AutonomousActivityCatalog.require(decision.selectedOptionId(), current); }
        catch (IllegalArgumentException stale) { return; }
        if (selected.changesWorld() || selected.ownerApprovalRequired()) return;

        BlockPos target = targetFor(level, owner, data, selected.kind(), snapshot.requestId());
        if (target == null || !validDelegatedTarget(level, owner, data, target)) return;
        long now = level.getGameTime();
        data.setAutonomousActivity(new AutonomousActivityPlan(AutonomousActivityPlan.State.SELECTED,
                selected.id(), selected.kind(), level.dimension().location().toString(), target,
                0, now, now, selected.reason()));
        data.remember(new MemoryEntry(now, "autonomous_plan", selected.id(), selected.reason(), 3));
        companion.setMode(CompanionMode.WORKING);
    }

    public static void clearRuntime() {
        decisionPending = false;
        decisionRequestedGameTime = 0;
    }

    public static String statusSuffix(CompanionSavedData data) {
        AutonomousActivityPlan plan = data.autonomousActivity();
        if (plan.state() == AutonomousActivityPlan.State.NONE) return " Autonomous activity: none.";
        return " Autonomous activity: " + plan.optionId().toLowerCase().replace('_', ' ')
                + " (" + plan.state().name().toLowerCase() + ").";
    }

    private static void requestChoice(ServerLevel level, ServerPlayer owner,
                                      ElvenCompanionEntity companion, CompanionSavedData data) {
        List<AutonomousActivityOption> options = options(data, companion, owner);
        if (options.isEmpty()) return;
        long requestId = data.nextRequestId();
        AutonomousActivitySnapshot snapshot = new AutonomousActivitySnapshot(requestId, owner.getUUID(),
                data.behaviorPreset().id(), companion.nutrition(), companion.stamina(),
                (int) DelegatedClaimService.delegatedCount(data, owner),
                data.autonomousActivity().optionId(), options);
        decisionPending = CompanionBrainCoordinator.requestAutonomousActivityDecision(snapshot);
        if (decisionPending) decisionRequestedGameTime = level.getGameTime();
    }

    private static List<AutonomousActivityOption> options(CompanionSavedData data,
                                                           ElvenCompanionEntity companion,
                                                           ServerPlayer owner) {
        return AutonomousActivityCatalog.optionsFor(data.behaviorPreset(), companion.nutrition(),
                companion.stamina(), (int) DelegatedClaimService.delegatedCount(data, owner),
                data.autonomousActivity().kind());
    }

    private static boolean eligible(MinecraftServer server, ServerLevel level, ServerPlayer owner,
                                    ElvenCompanionEntity companion, CompanionSavedData data) {
        BaseObjective base = data.baseObjective();
        return server.isSingleplayer() && owner.level() == level
                && data.leaseHeldBy(owner.getUUID(), level.getGameTime())
                && base.phase() == BaseObjective.Phase.MAINTAINING
                && base.dimensionId().equals(level.dimension().location().toString())
                && data.task().isNone() && !data.blueprintLedger().active()
                && companion.getHealth() > companion.getMaxHealth() * 0.25F
                && DelegatedClaimService.delegatedCount(data, owner) > 0;
    }

    private static boolean hasThreat(ElvenCompanionEntity companion) {
        return !companion.level().getEntitiesOfClass(Monster.class,
                companion.getBoundingBox().inflate(12.0D, 6.0D, 12.0D), Entity::isAlive).isEmpty();
    }

    private static BlockPos targetFor(ServerLevel level, ServerPlayer owner, CompanionSavedData data,
                                      AutonomousActivityKind kind, long requestId) {
        if (kind == AutonomousActivityKind.RECOVER_AT_BASE
                || kind == AutonomousActivityKind.INSPECT_BASE)
            return groundedLoaded(level, data.baseObjective().anchor());

        List<DelegatedClaim> claims = loadedClaims(level, owner, data);
        if (claims.isEmpty()) return null;
        DelegatedClaim claim;
        if (kind == AutonomousActivityKind.SURVEY_DISTRICT) {
            claim = claims.stream().min(Comparator.<DelegatedClaim>comparingLong(
                            candidate -> observedAt(data, candidate))
                    .thenComparingInt(DelegatedClaim::chunkX).thenComparingInt(DelegatedClaim::chunkZ)).orElse(null);
        } else if (kind == AutonomousActivityKind.PATROL_CLAIMS) {
            claim = claims.get(Math.floorMod((int) requestId, claims.size()));
        } else {
            return null;
        }
        if (claim == null) return null;
        ChunkPos chunk = new ChunkPos(claim.chunkX(), claim.chunkZ());
        return groundedLoaded(level, new BlockPos(chunk.getMinBlockX() + 8,
                data.baseObjective().anchor().getY(), chunk.getMinBlockZ() + 8));
    }

    private static List<DelegatedClaim> loadedClaims(ServerLevel level, ServerPlayer owner,
                                                     CompanionSavedData data) {
        String dimension = level.dimension().location().toString();
        return data.delegatedClaims().stream()
                .filter(claim -> claim.ownerUuid().equals(owner.getUUID())
                        && claim.dimensionId().equals(dimension))
                .filter(claim -> level.getChunkSource().getChunkNow(claim.chunkX(), claim.chunkZ()) != null)
                .filter(claim -> ClaimPermissionBridge.isClaimed(level,
                        new ChunkPos(claim.chunkX(), claim.chunkZ())))
                .sorted(Comparator.comparingInt(DelegatedClaim::chunkX)
                        .thenComparingInt(DelegatedClaim::chunkZ)).toList();
    }

    private static long observedAt(CompanionSavedData data, DelegatedClaim claim) {
        return data.observedChunks().stream()
                .filter(observed -> observed.dimensionId().equals(claim.dimensionId())
                        && observed.chunkX() == claim.chunkX() && observed.chunkZ() == claim.chunkZ())
                .mapToLong(ObservedChunk::observedGameTime).findFirst().orElse(0L);
    }

    private static BlockPos groundedLoaded(ServerLevel level, BlockPos position) {
        ChunkPos chunk = new ChunkPos(position);
        if (level.getChunkSource().getChunkNow(chunk.x, chunk.z) == null) return null;
        int y = level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
                position.getX(), position.getZ());
        return new BlockPos(position.getX(), y, position.getZ());
    }

    private static boolean validDelegatedTarget(ServerLevel level, ServerPlayer owner,
                                                CompanionSavedData data, BlockPos target) {
        String dimension = level.dimension().location().toString();
        ChunkPos chunk = new ChunkPos(target);
        boolean delegated = data.delegatedClaims().stream().anyMatch(claim ->
                claim.ownerUuid().equals(owner.getUUID()) && claim.dimensionId().equals(dimension)
                        && claim.chunkX() == chunk.x && claim.chunkZ() == chunk.z);
        return delegated && level.getChunkSource().getChunkNow(chunk.x, chunk.z) != null
                && ClaimPermissionBridge.isClaimed(level, chunk)
                && level.getWorldBorder().isWithinBounds(target);
    }

    private static void execute(ServerLevel level, ServerPlayer owner, ElvenCompanionEntity companion,
                                CompanionSavedData data, AutonomousActivityPlan plan) {
        long now = level.getGameTime();
        if (!plan.dimensionId().equals(level.dimension().location().toString())
                || !validDelegatedTarget(level, owner, data, plan.target())
                || now - plan.createdGameTime() > ACTIVITY_TIMEOUT_TICKS) {
            pause(companion, data, now, "target became unavailable");
            return;
        }
        if (companion.distanceToSqr(plan.target().getX() + 0.5D, plan.target().getY(),
                plan.target().getZ() + 0.5D) > 9.0D) {
            companion.getNavigation().moveTo(plan.target().getX() + 0.5D, plan.target().getY(),
                    plan.target().getZ() + 0.5D, 1.0D);
            if (plan.state() != AutonomousActivityPlan.State.TRAVELING)
                data.setAutonomousActivity(plan.advance(AutonomousActivityPlan.State.TRAVELING,
                        25, now, "traveling within delegated claims"));
            return;
        }

        companion.getNavigation().stop();
        if (plan.state() != AutonomousActivityPlan.State.OBSERVING) {
            data.setAutonomousActivity(plan.advance(AutonomousActivityPlan.State.OBSERVING,
                    75, now, "performing read-only inspection"));
            return;
        }
        long dwell = plan.kind() == AutonomousActivityKind.RECOVER_AT_BASE ? 200L : 40L;
        if (now - plan.updatedGameTime() < dwell) return;
        complete(level, companion, data, plan, now);
    }

    private static void complete(ServerLevel level, ElvenCompanionEntity companion,
                                 CompanionSavedData data, AutonomousActivityPlan plan, long now) {
        String detail = switch (plan.kind()) {
            case SURVEY_DISTRICT -> survey(level, plan.target());
            case INSPECT_BASE -> "foundation=" + BuiltInRegistries.BLOCK.getKey(
                    level.getBlockState(plan.target().below()).getBlock());
            case PATROL_CLAIMS -> "delegated boundary reached";
            case RECOVER_AT_BASE -> "quiet recovery interval complete";
            default -> "completed without world mutation";
        };
        data.setAutonomousActivity(plan.advance(AutonomousActivityPlan.State.COMPLETE,
                100, now, detail));
        data.remember(new MemoryEntry(now, "autonomous_complete", plan.optionId(), detail, 3));
        data.rememberFact("activity:last", plan.optionId() + ":" + detail);
        companion.setGuardPosition(data.baseObjective().anchor());
        companion.setMode(plan.kind() == AutonomousActivityKind.RECOVER_AT_BASE
                ? CompanionMode.WAITING : CompanionMode.GUARDING);
    }

    private static String survey(ServerLevel level, BlockPos center) {
        int minimum = Integer.MAX_VALUE;
        int maximum = Integer.MIN_VALUE;
        int wet = 0;
        for (int dx = -6; dx <= 6; dx += 6) {
            for (int dz = -6; dz <= 6; dz += 6) {
                int y = level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
                        center.getX() + dx, center.getZ() + dz);
                minimum = Math.min(minimum, y);
                maximum = Math.max(maximum, y);
                if (!level.getFluidState(new BlockPos(center.getX() + dx, y - 1,
                        center.getZ() + dz)).isEmpty()) wet++;
            }
        }
        return "relief=" + (maximum - minimum) + ",wet_samples=" + wet + "/9";
    }

    private static void pause(ElvenCompanionEntity companion, CompanionSavedData data,
                              long gameTime, String reason) {
        AutonomousActivityPlan plan = data.autonomousActivity();
        if (!plan.active()) return;
        companion.getNavigation().stop();
        data.setAutonomousActivity(plan.advance(AutonomousActivityPlan.State.PAUSED,
                plan.progress(), gameTime, reason));
        companion.setMode(CompanionMode.FOLLOWING);
    }
}

package com.continuityworks.alfheimcompanion.service;

import com.continuityworks.alfheimcompanion.brain.ClaimDistrictDecision;
import com.continuityworks.alfheimcompanion.brain.ClaimDistrictSnapshot;
import com.continuityworks.alfheimcompanion.brain.CompanionBrainCoordinator;
import com.continuityworks.alfheimcompanion.entity.ElvenCompanionEntity;
import com.continuityworks.alfheimcompanion.integration.ClaimPermissionBridge;
import com.continuityworks.alfheimcompanion.memory.ActiveTask;
import com.continuityworks.alfheimcompanion.memory.BaseObjective;
import com.continuityworks.alfheimcompanion.memory.CompanionSavedData;
import com.continuityworks.alfheimcompanion.memory.DelegatedClaim;
import com.continuityworks.alfheimcompanion.memory.MemoryEntry;
import com.continuityworks.alfheimcompanion.memory.ObservedChunk;
import com.continuityworks.alfheimcompanion.registry.ModItems;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.ChunkPos;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

/** Claim-Paper accounting and bounded district selection for integrated single-player worlds. */
public final class DelegatedClaimService {
    public static final int DISTRICT_RADIUS = 2;
    private static final int OBSERVE_INTERVAL_TICKS = 20;
    private static final int CLAIM_INTERVAL_TICKS = 200;
    private static final long FAILED_RETRY_TICKS = 1200L;
    private static final Map<String, Long> RETRY_AFTER = new HashMap<>();
    private static boolean decisionPending;
    private static long decisionRequestedGameTime;

    private DelegatedClaimService() {}

    public static void tick(MinecraftServer server) {
        if (server.getTickCount() % OBSERVE_INTERVAL_TICKS != 0) return;
        CompanionSavedData data = CompanionSavedData.get(server);
        ElvenCompanionEntity companion = CompanionSummonService.findLoaded(server,
                data.companionUuid().orElse(null));
        if (companion == null || !companion.isAlive() || !(companion.level() instanceof ServerLevel level)) return;
        ServerPlayer owner = companion.resolveOwner();
        if (owner == null || owner.level() != level) return;

        observeLoaded(level, owner.chunkPosition(), data);
        observeLoaded(level, companion.chunkPosition(), data);
        int papers = paperCount(companion);
        if (decisionPending && level.getGameTime() - decisionRequestedGameTime > 400L)
            decisionPending = false;
        int previousPapers = data.lastClaimPaperBalance();
        if (papers != previousPapers) {
            boolean resupplied = papers > previousPapers;
            data.setLastClaimPaperBalance(papers);
            if (resupplied && papers > 0 && !decisionPending
                    && data.baseObjective().phase() == BaseObjective.Phase.MAINTAINING
                    && delegatedCount(data, owner) > 0) {
                beginDistrictDecision(level, owner, data);
            }
        }
        if (!decisionPending && server.getTickCount() % CLAIM_INTERVAL_TICKS == 0)
            claimOne(server, level, owner, companion, data);
    }

    public static long delegatedCount(CompanionSavedData data, ServerPlayer owner) {
        return data.delegatedClaims().stream().filter(claim -> claim.ownerUuid().equals(owner.getUUID())).count();
    }

    public static int paperCount(ElvenCompanionEntity companion) {
        int total = 0;
        for (int slot = 0; slot < companion.inventory().getContainerSize(); slot++) {
            ItemStack stack = companion.inventory().getItem(slot);
            if (stack.is(ModItems.COMPANION_CLAIM_PAPER.get())) total += stack.getCount();
        }
        return total;
    }

    public static void clearRuntime() {
        RETRY_AFTER.clear();
        decisionPending = false;
        decisionRequestedGameTime = 0;
    }

    public static void applyDistrictDecision(MinecraftServer server, ClaimDistrictSnapshot snapshot,
                                             ClaimDistrictDecision decision) {
        decisionPending = false;
        decisionRequestedGameTime = 0;
        CompanionSavedData data = CompanionSavedData.get(server);
        ElvenCompanionEntity companion = CompanionSummonService.findLoaded(server,
                data.companionUuid().orElse(null));
        if (!server.isSingleplayer() || companion == null || !(companion.level() instanceof ServerLevel level)) return;
        ServerPlayer owner = companion.resolveOwner();
        BaseObjective objective = data.baseObjective();
        if (owner == null || !owner.getUUID().equals(snapshot.ownerUuid()) || owner.level() != level
                || objective.phase() != BaseObjective.Phase.MAINTAINING
                || !new ChunkPos(objective.anchor()).equals(snapshot.currentCenter())) return;

        if (decision.choice() == ClaimDistrictDecision.Choice.KEEP_DISTRICT
                || snapshot.candidateValue() + 20 < snapshot.currentValue()) {
            reply(owner, data, "I value the current district more highly, so I will use the new Claim Papers here.");
            return;
        }
        relocate(level, owner, companion, data, objective, snapshot.candidateCenter());
    }

    static List<ChunkPos> districtOrder(ChunkPos center) {
        List<ChunkPos> result = new ArrayList<>(25);
        for (int dx = -DISTRICT_RADIUS; dx <= DISTRICT_RADIUS; dx++)
            for (int dz = -DISTRICT_RADIUS; dz <= DISTRICT_RADIUS; dz++)
                result.add(new ChunkPos(center.x + dx, center.z + dz));
        result.sort(Comparator
                .comparingInt((ChunkPos position) -> Math.max(Math.abs(position.x - center.x),
                        Math.abs(position.z - center.z)))
                .thenComparingInt(position -> Math.abs(position.x - center.x) + Math.abs(position.z - center.z))
                .thenComparingInt(position -> position.x)
                .thenComparingInt(position -> position.z));
        return List.copyOf(result);
    }

    private static void observeLoaded(ServerLevel level, ChunkPos center, CompanionSavedData data) {
        String dimension = level.dimension().location().toString();
        long now = level.getGameTime();
        for (int dx = -DISTRICT_RADIUS; dx <= DISTRICT_RADIUS; dx++) {
            for (int dz = -DISTRICT_RADIUS; dz <= DISTRICT_RADIUS; dz++) {
                int x = center.x + dx;
                int z = center.z + dz;
                // getChunkNow never schedules a load or generation request.
                if (level.getChunkSource().getChunkNow(x, z) != null) data.observeChunk(dimension, x, z, now);
            }
        }
    }

    private static void beginDistrictDecision(ServerLevel level, ServerPlayer owner, CompanionSavedData data) {
        BaseObjective objective = data.baseObjective();
        ChunkPos current = new ChunkPos(objective.anchor());
        Optional<ScoredCenter> alternative = bestAlternative(level, owner, data, current);
        if (alternative.isEmpty()) return;
        int currentValue = scoreCenter(level, owner, data, current, true);
        ScoredCenter candidate = alternative.get();
        long requestId = data.nextRequestId();
        ClaimDistrictSnapshot snapshot = new ClaimDistrictSnapshot(requestId, owner.getUUID(),
                level.dimension().location().toString(), current, candidate.position(), currentValue,
                candidate.value(), data.behaviorPreset().id(),
                "established base; delegated=" + claimsInDistrict(data, owner, current),
                "observed alternative; open_slots=" + openObservedSlots(level, data, candidate.position()));
        decisionPending = CompanionBrainCoordinator.requestClaimDistrictDecision(snapshot);
        if (decisionPending) decisionRequestedGameTime = level.getGameTime();
    }

    private static Optional<ScoredCenter> bestAlternative(ServerLevel level, ServerPlayer owner,
                                                           CompanionSavedData data, ChunkPos current) {
        String dimension = level.dimension().location().toString();
        return data.observedChunks().stream()
                .filter(observed -> observed.dimensionId().equals(dimension))
                .map(observed -> new ChunkPos(observed.chunkX(), observed.chunkZ()))
                .filter(candidate -> chebyshev(candidate, current) > DISTRICT_RADIUS * 2)
                .filter(candidate -> !ClaimPermissionBridge.isClaimed(level, candidate))
                .filter(candidate -> level.getWorldBorder().isWithinBounds(centerBlock(candidate, 64)))
                .map(candidate -> new ScoredCenter(candidate, scoreCenter(level, owner, data, candidate, false)))
                .filter(candidate -> candidate.value() >= 10)
                .max(Comparator.comparingInt(ScoredCenter::value)
                        .thenComparingInt(candidate -> -candidate.position().x)
                        .thenComparingInt(candidate -> -candidate.position().z));
    }

    private static int scoreCenter(ServerLevel level, ServerPlayer owner, CompanionSavedData data,
                                   ChunkPos center, boolean current) {
        int open = openObservedSlots(level, data, center);
        int delegated = claimsInDistrict(data, owner, center);
        int value = open * 2 + delegated * 2;
        if (current && data.baseObjective().established()) value += 25;
        if (!current) value -= Math.min(20, chebyshev(center, owner.chunkPosition()) / 4);
        return Math.max(0, Math.min(100, value));
    }

    private static int openObservedSlots(ServerLevel level, CompanionSavedData data, ChunkPos center) {
        String dimension = level.dimension().location().toString();
        int count = 0;
        for (ChunkPos candidate : districtOrder(center)) {
            if (data.hasObservedChunk(dimension, candidate.x, candidate.z)
                    && !ClaimPermissionBridge.isClaimed(level, candidate)
                    && level.getWorldBorder().isWithinBounds(centerBlock(candidate, 64))) count++;
        }
        return count;
    }

    private static int claimsInDistrict(CompanionSavedData data, ServerPlayer owner, ChunkPos center) {
        String dimension = owner.level().dimension().location().toString();
        return (int) data.delegatedClaims().stream()
                .filter(claim -> claim.ownerUuid().equals(owner.getUUID()) && claim.dimensionId().equals(dimension))
                .filter(claim -> chebyshev(new ChunkPos(claim.chunkX(), claim.chunkZ()), center) <= DISTRICT_RADIUS)
                .count();
    }

    private static void claimOne(MinecraftServer server, ServerLevel level, ServerPlayer owner,
                                 ElvenCompanionEntity companion, CompanionSavedData data) {
        if (!server.isSingleplayer() || !data.leaseHeldBy(owner.getUUID(), level.getGameTime())) return;
        BaseObjective objective = data.baseObjective();
        if (!objective.exists() || objective.phase() == BaseObjective.Phase.PAUSED
                || !objective.dimensionId().equals(level.dimension().location().toString())
                || paperCount(companion) <= 0) return;
        ChunkPos center = new ChunkPos(objective.anchor());
        for (ChunkPos candidate : districtOrder(center)) {
            if (tryClaim(level, owner, companion, data, objective, candidate)) return;
        }
    }

    private static boolean tryClaim(ServerLevel level, ServerPlayer owner, ElvenCompanionEntity companion,
                                    CompanionSavedData data, BaseObjective objective, ChunkPos candidate) {
        String dimension = level.dimension().location().toString();
        String key = DelegatedClaim.key(dimension, candidate.x, candidate.z);
        long now = level.getGameTime();
        if (RETRY_AFTER.getOrDefault(key, 0L) > now
                || !data.hasObservedChunk(dimension, candidate.x, candidate.z)
                || ClaimPermissionBridge.isClaimed(level, candidate)
                || !level.getWorldBorder().isWithinBounds(centerBlock(candidate, objective.anchor().getY())))
            return false;
        ClaimPermissionBridge.ClaimAttempt result = ClaimPermissionBridge.claim(owner, level, candidate);
        if (!result.success()) {
            RETRY_AFTER.put(key, now + FAILED_RETRY_TICKS);
            return false;
        }
        if (!consumePaper(companion)) {
            reply(owner, data, "A claim succeeded, but paper accounting changed unexpectedly. I stopped expanding.");
            return true;
        }
        data.setLastClaimPaperBalance(paperCount(companion));
        data.recordDelegatedClaim(new DelegatedClaim(owner.getUUID(), dimension, candidate.x,
                candidate.z, objective.purpose(), now));
        data.remember(new MemoryEntry(now, "delegated_claim", candidate.x + "," + candidate.z,
                objective.purpose(), 7));
        reply(owner, data, "I used one Claim Paper to add chunk " + candidate.x + ", "
                + candidate.z + " to our base district.");
        return true;
    }

    private static void relocate(ServerLevel level, ServerPlayer owner, ElvenCompanionEntity companion,
                                 CompanionSavedData data, BaseObjective objective, ChunkPos destination) {
        String dimension = level.dimension().location().toString();
        if (paperCount(companion) <= 0 || !data.hasObservedChunk(dimension, destination.x, destination.z)
                || ClaimPermissionBridge.isClaimed(level, destination)) return;
        ClaimPermissionBridge.ClaimAttempt preview = ClaimPermissionBridge.previewClaim(owner, level, destination);
        if (!preview.success()) return;
        ClaimPermissionBridge.ClaimAttempt claimed = ClaimPermissionBridge.claim(owner, level, destination);
        if (!claimed.success() || !consumePaper(companion)) return;
        long now = level.getGameTime();
        data.recordDelegatedClaim(new DelegatedClaim(owner.getUUID(), dimension, destination.x,
                destination.z, objective.purpose(), now));

        ChunkPos oldCenter = new ChunkPos(objective.anchor());
        List<DelegatedClaim> retiring = data.delegatedClaims().stream()
                .filter(claim -> claim.ownerUuid().equals(owner.getUUID()) && claim.dimensionId().equals(dimension))
                .filter(claim -> !(claim.chunkX() == destination.x && claim.chunkZ() == destination.z))
                .filter(claim -> chebyshev(new ChunkPos(claim.chunkX(), claim.chunkZ()), oldCenter) <= DISTRICT_RADIUS)
                .toList();
        int released = 0;
        for (DelegatedClaim claim : retiring) {
            ClaimPermissionBridge.ClaimAttempt result = ClaimPermissionBridge.unclaim(owner, level,
                    new ChunkPos(claim.chunkX(), claim.chunkZ()));
            if (!result.success()) continue;
            data.removeDelegatedClaim(dimension, claim.chunkX(), claim.chunkZ());
            released++;
        }

        BlockPos anchor = centerBlock(destination, objective.anchor().getY());
        BaseObjective moved = new BaseObjective(BaseObjective.Phase.SURVEY, dimension, anchor,
                objective.purpose(), now, now);
        data.setBaseObjective(moved);
        data.setTask(new ActiveTask(ActiveTask.Kind.BASE, BaseObjective.Phase.SURVEY.name(),
                moved.purpose(), 1, now), null);
        data.setLastClaimPaperBalance(paperCount(companion));
        reply(owner, data, "I chose to relocate the district to chunk " + destination.x + ", "
                + destination.z + ". The new center is claimed and " + released
                + " former delegated claim" + (released == 1 ? " was" : "s were") + " released.");
    }

    private static boolean consumePaper(ElvenCompanionEntity companion) {
        for (int slot = 0; slot < companion.inventory().getContainerSize(); slot++) {
            ItemStack stack = companion.inventory().getItem(slot);
            if (!stack.is(ModItems.COMPANION_CLAIM_PAPER.get())) continue;
            stack.shrink(1);
            companion.inventory().setChanged();
            return true;
        }
        return false;
    }

    private static int chebyshev(ChunkPos first, ChunkPos second) {
        return Math.max(Math.abs(first.x - second.x), Math.abs(first.z - second.z));
    }

    private static BlockPos centerBlock(ChunkPos chunk, int y) {
        return new BlockPos(chunk.getMinBlockX() + 8, y, chunk.getMinBlockZ() + 8);
    }

    private static void reply(ServerPlayer owner, CompanionSavedData data, String message) {
        owner.sendSystemMessage(Component.literal("§d[" + data.companionName() + "] §f" + message));
    }

    private record ScoredCenter(ChunkPos position, int value) {}
}

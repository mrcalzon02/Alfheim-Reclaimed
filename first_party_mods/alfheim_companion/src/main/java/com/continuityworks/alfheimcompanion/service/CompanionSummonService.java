package com.continuityworks.alfheimcompanion.service;

import com.continuityworks.alfheimcompanion.entity.ElvenCompanionEntity;
import com.continuityworks.alfheimcompanion.memory.CompanionSavedData;
import com.continuityworks.alfheimcompanion.memory.MemoryEntry;
import com.continuityworks.alfheimcompanion.personality.DialogueBank;
import com.continuityworks.alfheimcompanion.brain.CompanionBrainCoordinator;
import com.continuityworks.alfheimcompanion.integration.CombatProfileBridge;
import com.continuityworks.alfheimcompanion.registry.ModEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.phys.Vec3;

import java.util.UUID;

public final class CompanionSummonService {
    private CompanionSummonService() {}

    public static void summonOrRecall(ServerPlayer owner) {
        MinecraftServer server = owner.server;
        CompanionSavedData data = CompanionSavedData.get(server);
        long now = server.overworld().getGameTime();
        if (data.leaseHeldByOther(owner.getUUID(), now)) {
            owner.sendSystemMessage(Component.literal("§d[" + data.companionName()
                    + "] §fSorry, I’m currently busy!"));
            return;
        }
        // A dead requester may not clear another player's task, name, or carried inventory.
        if (!data.getOrCreatePlayerBinding(owner.getUUID(), now).alive()) {
            owner.sendSystemMessage(Component.literal("§d[Hollow Court] §fYour companion has fallen. "
                    + "Use /alfheimcompanion reset to create a new binding."));
            return;
        }
        // Probe a destination BEFORE the handoff can save, clear, or reassign anyone's
        // inventory. A recall from a crowded area must not strand the previous owner.
        ElvenCompanionEntity loadedCompanion = findLoaded(server, data.companionUuid().orElse(null));
        Vec3 loadedDestination = loadedCompanion == null
                ? null : findSafeSummonPosition(owner, loadedCompanion);
        if (loadedCompanion != null && loadedDestination == null) {
            owner.sendSystemMessage(Component.literal(
                    "Cannot recall companion: no safe, dry landing within three blocks. "
                    + "Move to clear solid ground and try again."));
            return;
        }
        boolean changingLessee = data.ownerUuid().isPresent()
                && !data.ownerUuid().get().equals(owner.getUUID());
        UUID previousOwner = data.ownerUuid().orElse(null);
        boolean ownerMatches = loadedCompanion != null && previousOwner != null
                && previousOwner.equals(loadedCompanion.ownerUuid());
        CompanionHandoffRules.Decision decision = CompanionHandoffRules.evaluate(
                changingLessee, loadedCompanion != null,
                data.mode() == com.continuityworks.alfheimcompanion.memory.CompanionMode.DISMISSED,
                ownerMatches);
        // These two protections apply to ALL players, including the current owner.
        // Otherwise an unloaded active entity can be replaced while still carrying items.
        if (decision == CompanionHandoffRules.Decision.BLOCK_UNLOADED_ACTIVE) {
            BlockPos lastKnown = data.lastPosition();
            owner.sendSystemMessage(Component.literal(
                    "Your companion is still active but not loaded. Last recorded: "
                    + data.dimensionId() + " at " + lastKnown.getX() + ", "
                    + lastKnown.getY() + ", " + lastKnown.getZ()
                    + ". Load that area or ask an operator to investigate. No replacement was created."));
            return;
        }
        if (decision == CompanionHandoffRules.Decision.BLOCK_OWNER_MISMATCH) {
            owner.sendSystemMessage(Component.literal(
                    "Companion owner mismatch between saved lease and loaded entity. "
                    + "Recall refused to protect inventory; operator investigation required."));
            return;
        }
        // A failed admission or transfer must not alter the saved lease or the previous
        // player's inventory and tasks. Commit those transitions only after success.
        ElvenCompanionEntity companion = loadedCompanion;
        boolean newlyCreated = false;

        if (companion == null) {
            companion = ModEntities.ELVEN_COMPANION.get().create(owner.serverLevel());
            if (companion == null) {
                owner.sendSystemMessage(Component.translatable("message.alfheim_companion.summon_failed"));
                return;
            }
            companion.bindOwner(owner.getUUID());
            // Persisted equipment must not be consumed until Forge accepts the entity.
            Vec3 destination = findSafeSummonPosition(owner, companion);
            if (destination == null) {
                owner.sendSystemMessage(Component.literal(
                        "Cannot summon companion: no safe, dry landing within three blocks. "
                        + "Move to clear solid ground and try again."));
                return;
            }
            companion.moveTo(destination.x, destination.y, destination.z, owner.getYRot(), 0.0F);
            companion.setCustomName(Component.literal(
                    data.playerBinding(owner.getUUID()).orElseThrow().name()));
            companion.setCustomNameVisible(true);
            UUID candidateId = companion.getUUID();
            if (!data.beginCompanionAdmission(candidateId, owner.getUUID())) {
                owner.sendSystemMessage(Component.literal(
                        "Companion summon already in progress; please retry."));
                return;
            }
            boolean admitted;
            try {
                // EntityJoinLevelEvent can inspect the reservation; no saved UUID is touched.
                admitted = owner.serverLevel().addFreshEntity(companion);
            } finally {
                data.endCompanionAdmission(candidateId, owner.getUUID());
            }
            if (!admitted) {
                owner.sendSystemMessage(Component.translatable("message.alfheim_companion.summon_failed"));
                return;
            }
            newlyCreated = true;
        } else {
            // Keep previous entity ownership unchanged until cross-dimensional transfer succeeds.
            if (companion.level() != owner.level()) {
                Entity moved = companion.changeDimension(owner.serverLevel());
                if (!(moved instanceof ElvenCompanionEntity movedCompanion)
                        || !movedCompanion.isAlive() || movedCompanion.level() != owner.level()) {
                    owner.sendSystemMessage(Component.literal(
                            "Cross-dimensional companion recall failed; no new position was saved. Please retry."));
                    return;
                }
                companion = movedCompanion;
            }
            Vec3 destination = loadedDestination;
            companion.teleportTo(destination.x, destination.y, destination.z);
            if (changingLessee && decision == CompanionHandoffRules.Decision.SAVE_LOADED_COMPANION
                    && !CompanionDeathInventoryService.retainForDismiss(companion, data, previousOwner)) {
                owner.sendSystemMessage(Component.literal(
                        "Companion handoff blocked: unable to preserve previous owner's inventory."));
                return;
            }
            companion.bindOwner(owner.getUUID());
        }

        if (changingLessee) {
            BlueprintLifecycleService.cancel(server);
            CompanionBrainCoordinator.deactivate();
            data.setTask(com.continuityworks.alfheimcompanion.memory.ActiveTask.NONE, null);
            data.clearOwnerContext();
        }
        // The persistent identity, owner, and lease are recorded only after successful
        // insertion or recall; an admission failure returns without changing them.
        data.activatePlayerBinding(owner.getUUID(), now);
        data.claimOrRefreshLease(owner.getUUID(), now);
        data.bind(companion.getUUID(), owner.getUUID(),
                owner.level().dimension().location().toString(), companion.blockPosition());
        companion.setCustomName(Component.literal(data.companionName()));
        companion.setCustomNameVisible(true);
        if (newlyCreated || changingLessee) data.restoreFallenInventory(owner.getUUID(), companion);
        TeleportEffects.play(companion);
        int agitation = data.recordSummon(owner.level().getGameTime());
        if (newlyCreated) data.remember(new MemoryEntry(owner.level().getGameTime(), "summon",
                owner.getName().getString(), "First summoned or restored to the world", 8));

        try {
            CombatProfileBridge.synchronize(owner, companion);
        } catch (RuntimeException | LinkageError error) {
            com.continuityworks.alfheimcompanion.AlfheimCompanion.LOGGER.warn(
                    "Optional combat profile synchronization failed during summon", error);
        }
        owner.sendSystemMessage(Component.translatable("message.alfheim_companion.summoned", data.companionName()));
        QuestMemoryService.refresh(owner, data);
        CompanionBrainCoordinator.warmup();
        DialogueBank.Moment moment = agitation >= 3
                ? DialogueBank.Moment.SUMMON_CRANKY : DialogueBank.Moment.SUMMON;
        owner.sendSystemMessage(Component.literal("§d[" + data.companionName() + "] §f"
                + DialogueBank.line(moment, owner.level().getGameTime() + agitation,
                data.companionName(), data.moodIndex())));
    }

    public static void dismiss(ServerPlayer owner) {
        CompanionSavedData data = CompanionSavedData.get(owner.server);
        if (data.ownerUuid().isPresent() && !data.ownerUuid().get().equals(owner.getUUID())) {
            owner.sendSystemMessage(Component.translatable("message.alfheim_companion.not_owner"));
            return;
        }
        ElvenCompanionEntity companion = findLoaded(owner.server, data.companionUuid().orElse(null));
        if (companion == null
                && data.mode() != com.continuityworks.alfheimcompanion.memory.CompanionMode.DISMISSED) {
            owner.sendSystemMessage(Component.literal(
                    "Cannot dismiss: your active companion is not loaded. "
                    + "Return to its last location or recall it before dismissing; "
                    + "its carried items have not been altered."));
            return;
        }
        if (companion != null) {
            // Discard does not fire LivingDeathEvent. Preserve cargo and equipped items
            // first, otherwise every ordinary dismissal silently destroys player gear.
            if (!CompanionDeathInventoryService.retainForDismiss(companion, data, owner.getUUID())) {
                owner.sendSystemMessage(Component.literal(
                        "Companion ownership mismatch; dismissal cancelled to protect carried items."));
                return;
            }
            owner.sendSystemMessage(Component.literal("§d[" + data.companionName() + "] §f"
                    + DialogueBank.line(DialogueBank.Moment.DISMISS, owner.level().getGameTime(), data.companionName())));
            TeleportEffects.play(companion);
            CompanionChunkTickets.release(companion.getUUID());
            companion.discard();
        }
        BlueprintLifecycleService.cancel(owner.server);
        CompanionBrainCoordinator.deactivate();
        data.releaseLease();
        data.dismiss();
        owner.sendSystemMessage(Component.translatable("message.alfheim_companion.dismissed", data.companionName()));
    }

    public static ElvenCompanionEntity findLoaded(MinecraftServer server, UUID companionUuid) {
        if (companionUuid == null) return null;
        for (ServerLevel level : server.getAllLevels()) {
            Entity entity = level.getEntity(companionUuid);
            if (entity instanceof ElvenCompanionEntity companion && companion.isAlive()) return companion;
        }
        return null;
    }

    private static Vec3 findSafeSummonPosition(ServerPlayer owner, ElvenCompanionEntity companion) {
        ServerLevel level = owner.serverLevel();
        BlockPos origin = owner.blockPosition();
        Vec3 original = companion.position();
        try {
            // Inspect each near-to-far square ring once; no random duplicates and no
            // unchecked fallback inside walls, liquids, fire, or unsupported terrain.
            for (CompanionLandingPlan.Offset offset : CompanionLandingPlan.candidates()) {
                BlockPos candidate = origin.offset(offset.dx(), offset.dy(), offset.dz());
                BlockPos floorPos = candidate.below();
                BlockState floor = level.getBlockState(floorPos);
                if (!floor.isFaceSturdy(level, floorPos, Direction.UP)
                        || floor.is(Blocks.MAGMA_BLOCK)
                        || floor.is(Blocks.CAMPFIRE)
                        || floor.is(Blocks.SOUL_CAMPFIRE)) continue;
                if (unsafeLandingBlock(level.getBlockState(candidate))
                        || unsafeLandingBlock(level.getBlockState(candidate.above()))) continue;

                companion.setPos(candidate.getX() + 0.5D, candidate.getY(), candidate.getZ() + 0.5D);
                if (level.noCollision(companion)) return companion.position();
            }
            // The caller must refuse to summon/recall when no viable position exists.
            return null;
        } finally {
            // Probing a loaded companion must not silently move it when all checks fail.
            companion.setPos(original.x, original.y, original.z);
        }
    }

    private static boolean unsafeLandingBlock(BlockState state) {
        return !state.getFluidState().isEmpty()
                || state.is(Blocks.FIRE)
                || state.is(Blocks.SOUL_FIRE);
    }
}

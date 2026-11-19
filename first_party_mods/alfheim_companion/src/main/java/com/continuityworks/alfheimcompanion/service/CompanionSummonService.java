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
        boolean changingLessee = data.ownerUuid().isPresent()
                && !data.ownerUuid().get().equals(owner.getUUID());
        if (changingLessee) {
            ElvenCompanionEntity previous = findLoaded(server, data.companionUuid().orElse(null));
            UUID previousOwner = data.ownerUuid().orElse(null);
            boolean ownerMatches = previous != null && previousOwner != null
                    && previousOwner.equals(previous.ownerUuid());
            CompanionHandoffRules.Decision decision = CompanionHandoffRules.evaluate(
                    true, previous != null,
                    data.mode() == com.continuityworks.alfheimcompanion.memory.CompanionMode.DISMISSED,
                    ownerMatches);
            if (decision == CompanionHandoffRules.Decision.BLOCK_UNLOADED_ACTIVE) {
                owner.sendSystemMessage(Component.literal(
                        "Companion handoff blocked: the active companion is in unloaded chunks. "
                        + "Load its last location or have the previous player dismiss it first."));
                return;
            }
            if (decision == CompanionHandoffRules.Decision.BLOCK_OWNER_MISMATCH) {
                owner.sendSystemMessage(Component.literal(
                        "Companion handoff blocked: the entity's owner does not match its saved lease."));
                return;
            }
            if (decision == CompanionHandoffRules.Decision.SAVE_LOADED_COMPANION
                    && !CompanionDeathInventoryService.retainForDismiss(previous, data, previousOwner)) {
                owner.sendSystemMessage(Component.literal(
                        "Companion handoff blocked: unable to preserve previous owner's inventory."));
                return;
            }
            // Previous owner's equipment is safely persisted before the new lease is granted.
            BlueprintLifecycleService.cancel(server);
            CompanionBrainCoordinator.deactivate();
            data.setTask(com.continuityworks.alfheimcompanion.memory.ActiveTask.NONE, null);
            data.clearOwnerContext();
        }
        data.activatePlayerBinding(owner.getUUID(), now);
        data.claimOrRefreshLease(owner.getUUID(), now);
        int agitation = data.recordSummon(owner.level().getGameTime());
        ElvenCompanionEntity companion = findLoaded(server, data.companionUuid().orElse(null));

        if (companion == null) {
            companion = ModEntities.ELVEN_COMPANION.get().create(owner.serverLevel());
            if (companion == null) {
                owner.sendSystemMessage(Component.translatable("message.alfheim_companion.summon_failed"));
                return;
            }
            companion.bindOwner(owner.getUUID());
            // Persisted equipment must not be consumed until Forge accepts the entity.
            Vec3 destination = findSafeSummonPosition(owner, companion);
            companion.moveTo(destination.x, destination.y, destination.z, owner.getYRot(), 0.0F);
            data.bind(companion.getUUID(), owner.getUUID(),
                    owner.level().dimension().location().toString(), companion.blockPosition());
            companion.setCustomName(Component.literal(data.companionName()));
            companion.setCustomNameVisible(true);
            if (!owner.serverLevel().addFreshEntity(companion)) {
                data.releaseLease();
                data.dismiss();
                owner.sendSystemMessage(Component.translatable("message.alfheim_companion.summon_failed"));
                return;
            }
            data.restoreFallenInventory(owner.getUUID(), companion);
            TeleportEffects.play(companion);
            data.remember(new MemoryEntry(owner.level().getGameTime(), "summon", owner.getName().getString(),
                    "First summoned or restored to the world", 8));
        } else {
            companion.bindOwner(owner.getUUID());
            TeleportEffects.play(companion);
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
            Vec3 destination = findSafeSummonPosition(owner, companion);
            companion.teleportTo(destination.x, destination.y, destination.z);
            // On lease transfer the old equipment was saved under the previous player;
            // restore only this player's own cached equipment to the now-accepted entity.
            if (changingLessee) data.restoreFallenInventory(owner.getUUID(), companion);
            TeleportEffects.play(companion);
            data.bind(companion.getUUID(), owner.getUUID(),
                    owner.level().dimension().location().toString(), companion.blockPosition());
            companion.setCustomName(Component.literal(data.companionName()));
            companion.setCustomNameVisible(true);
        }

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
        for (int attempt = 0; attempt < 24; attempt++) {
            int dx = level.random.nextInt(11) - 5;
            int dz = level.random.nextInt(11) - 5;
            if (dx * dx + dz * dz > 25 || dx * dx + dz * dz < 2) continue;
            for (int dy : new int[]{0, 1, -1, 2, -2}) {
                BlockPos candidate = origin.offset(dx, dy, dz);
                companion.setPos(candidate.getX() + 0.5D, candidate.getY(), candidate.getZ() + 0.5D);
                boolean floor = level.getBlockState(candidate.below()).isFaceSturdy(level, candidate.below(), Direction.UP);
                if (floor && level.noCollision(companion)) return companion.position();
            }
        }
        return owner.position().add(1.0D, 0.0D, 1.0D);
    }
}

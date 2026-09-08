package com.continuityworks.alfheimcompanion.service;

import com.continuityworks.alfheimcompanion.entity.ElvenCompanionEntity;
import com.continuityworks.alfheimcompanion.memory.CompanionSavedData;
import com.continuityworks.alfheimcompanion.memory.MemoryEntry;
import com.continuityworks.alfheimcompanion.personality.DialogueBank;
import com.continuityworks.alfheimcompanion.brain.CompanionBrainCoordinator;
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
        int agitation = data.recordSummon(owner.level().getGameTime());
        ElvenCompanionEntity companion = findLoaded(server, data.companionUuid().orElse(null));

        if (companion == null) {
            companion = ModEntities.ELVEN_COMPANION.get().create(owner.serverLevel());
            if (companion == null) {
                owner.sendSystemMessage(Component.translatable("message.alfheim_companion.summon_failed"));
                return;
            }
            companion.bindOwner(owner.getUUID());
            Vec3 destination = findSafeSummonPosition(owner, companion);
            companion.moveTo(destination.x, destination.y, destination.z, owner.getYRot(), 0.0F);
            data.bind(companion.getUUID(), owner.getUUID(),
                    owner.level().dimension().location().toString(), companion.blockPosition());
            companion.setCustomName(Component.literal(data.companionName()));
            companion.setCustomNameVisible(true);
            if (!owner.serverLevel().addFreshEntity(companion)) {
                data.dismiss();
                owner.sendSystemMessage(Component.translatable("message.alfheim_companion.summon_failed"));
                return;
            }
            TeleportEffects.play(companion);
            data.remember(new MemoryEntry(owner.level().getGameTime(), "summon", owner.getName().getString(),
                    "First summoned or restored to the world", 8));
        } else {
            companion.bindOwner(owner.getUUID());
            TeleportEffects.play(companion);
            if (companion.level() != owner.level()) {
                Entity moved = companion.changeDimension(owner.serverLevel());
                if (moved instanceof ElvenCompanionEntity movedCompanion) companion = movedCompanion;
            }
            Vec3 destination = findSafeSummonPosition(owner, companion);
            companion.teleportTo(destination.x, destination.y, destination.z);
            TeleportEffects.play(companion);
            data.bind(companion.getUUID(), owner.getUUID(),
                    owner.level().dimension().location().toString(), companion.blockPosition());
            companion.setCustomName(Component.literal(data.companionName()));
            companion.setCustomNameVisible(true);
        }

        owner.sendSystemMessage(Component.translatable("message.alfheim_companion.summoned", data.companionName()));
        DialogueBank.Moment moment = agitation >= 3
                ? DialogueBank.Moment.SUMMON_CRANKY : DialogueBank.Moment.SUMMON;
        owner.sendSystemMessage(Component.literal("§d[" + data.companionName() + "] §f"
                + DialogueBank.line(moment, owner.level().getGameTime() + agitation)));
    }

    public static void dismiss(ServerPlayer owner) {
        CompanionSavedData data = CompanionSavedData.get(owner.server);
        if (data.ownerUuid().isPresent() && !data.ownerUuid().get().equals(owner.getUUID())) {
            owner.sendSystemMessage(Component.translatable("message.alfheim_companion.not_owner"));
            return;
        }
        ElvenCompanionEntity companion = findLoaded(owner.server, data.companionUuid().orElse(null));
        if (companion != null) {
            owner.sendSystemMessage(Component.literal("§d[" + data.companionName() + "] §f"
                    + DialogueBank.line(DialogueBank.Moment.DISMISS, owner.level().getGameTime())));
            TeleportEffects.play(companion);
            CompanionChunkTickets.release(companion.getUUID());
            companion.discard();
        }
        CompanionBrainCoordinator.deactivate();
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

package com.continuityworks.alfheimcompanion.service;

import com.continuityworks.alfheimcompanion.api.blueprint.BlueprintProvider;
import com.continuityworks.alfheimcompanion.entity.ElvenCompanionEntity;
import com.continuityworks.alfheimcompanion.integration.ClaimPermissionBridge;
import com.continuityworks.alfheimcompanion.integration.ContinuityWorksBridge;
import com.continuityworks.alfheimcompanion.memory.ActiveTask;
import com.continuityworks.alfheimcompanion.memory.BlueprintLedger;
import com.continuityworks.alfheimcompanion.memory.CompanionMode;
import com.continuityworks.alfheimcompanion.memory.CompanionSavedData;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.TimeUnit;

/** Owner-approved, bounded bridge between Continuity Works proposals and player-like block actions. */
public final class BlueprintLifecycleService {
    private static final int MAX_PLACEMENTS = 8192;
    private static final BlueprintProvider.Bounds MAX_BOUNDS = new BlueprintProvider.Bounds(48, 32, 48);
    private static Pending pending;

    private BlueprintLifecycleService() {}

    public static void request(ServerPlayer owner, ElvenCompanionEntity companion, String purpose) {
        BlueprintProvider provider = ContinuityWorksBridge.provider().orElse(null);
        CompanionSavedData data = CompanionSavedData.get(owner.server);
        if (provider == null || !provider.capabilities().contains(BlueprintProvider.Capability.GENERATION)) {
            reply(owner, data, "The Continuity Works blueprint generator is not connected.");
            return;
        }
        if (data.blueprintLedger().active()) {
            reply(owner, data, "A blueprint is already pending. Approve, reject, or cancel it first.");
            return;
        }

        UUID requestId = UUID.randomUUID();
        BlockPos origin = owner.blockPosition().relative(owner.getDirection(), 3);
        BlueprintProvider.BlueprintRequest request = new BlueprintProvider.BlueprintRequest(requestId,
                companion.getUUID(), owner.getUUID(), owner.level().dimension().location().toString(), purpose,
                origin, owner.getDirection(), MAX_BOUNDS, materials(owner, companion),
                List.of(new BlueprintProvider.SiteCandidate("owner-facing", origin, owner.getDirection(), 100)),
                Set.of());
        data.setBlueprintLedger(new BlueprintLedger(requestId, null, BlueprintLedger.State.REQUESTED,
                purpose, "", 0, 0, "Generating proposal", owner.level().getGameTime()));
        provider.generate(request).orTimeout(15, TimeUnit.SECONDS).whenComplete((proposal, error) ->
                owner.server.execute(() -> acceptProposal(owner.server, provider, request, proposal, error)));
    }

    public static void approve(ServerPlayer owner, ElvenCompanionEntity companion) {
        CompanionSavedData data = CompanionSavedData.get(owner.server);
        BlueprintLedger ledger = data.blueprintLedger();
        if (pending == null || ledger.state() != BlueprintLedger.State.PREVIEW
                || !pending.ownerUuid.equals(owner.getUUID()) || !pending.request.requestId().equals(ledger.requestId())) {
            reply(owner, data, ledger.state() == BlueprintLedger.State.PAUSED
                    ? "That preview was interrupted by a restart. Ask me to build it again."
                    : "There is no current blueprint preview to approve.");
            return;
        }
        Validation validation = validate(pending.provider, pending.proposal, owner, companion);
        if (!validation.valid) {
            fail(data, owner, "Approval failed: " + validation.message);
            return;
        }
        pending.index = 0;
        data.setBlueprintLedger(ledgerWith(data, BlueprintLedger.State.EXECUTING, 0, "Owner approved",
                owner.level().getGameTime()));
        companion.setMode(CompanionMode.WORKING);
        reply(owner, data, "Approved. I will use real inventory and recheck claims before every block.");
    }

    public static void reject(ServerPlayer owner) {
        CompanionSavedData data = CompanionSavedData.get(owner.server);
        BlueprintLedger ledger = data.blueprintLedger();
        if (!ledger.active()) {
            reply(owner, data, "There is no active blueprint to reject.");
            return;
        }
        ContinuityWorksBridge.provider().ifPresent(provider -> {
            if (ledger.requestId() != null) provider.cancel(ledger.requestId());
        });
        pending = null;
        data.setBlueprintLedger(ledgerWith(data, BlueprintLedger.State.REJECTED,
                ledger.completedPlacements(), "Owner rejected", owner.level().getGameTime()));
        data.setTask(ActiveTask.NONE, null);
        reply(owner, data, "The blueprint has been rejected. No further blocks will be changed.");
    }

    public static void cancel(MinecraftServer server) {
        CompanionSavedData data = CompanionSavedData.get(server);
        BlueprintLedger ledger = data.blueprintLedger();
        ContinuityWorksBridge.provider().ifPresent(provider -> {
            if (ledger.requestId() != null) provider.cancel(ledger.requestId());
        });
        pending = null;
        if (ledger.active()) data.setBlueprintLedger(ledgerWith(data, BlueprintLedger.State.REJECTED,
                ledger.completedPlacements(), "Cancelled", server.overworld().getGameTime()));
    }

    public static void tick(MinecraftServer server) {
        if (pending == null || server.getTickCount() % 4 != 0) return;
        CompanionSavedData data = CompanionSavedData.get(server);
        if (data.blueprintLedger().state() != BlueprintLedger.State.EXECUTING) return;
        ElvenCompanionEntity companion = CompanionSummonService.findLoaded(server,
                data.companionUuid().orElse(null));
        ServerPlayer owner = server.getPlayerList().getPlayer(pending.ownerUuid);
        if (companion == null || owner == null || !(companion.level() instanceof ServerLevel level)
                || owner.level() != level) return;

        if (pending.index >= pending.proposal.placements().size()) {
            data.setBlueprintLedger(ledgerWith(data, BlueprintLedger.State.COMPLETE, pending.index, "Complete",
                    level.getGameTime()));
            data.setTask(ActiveTask.NONE, pending.proposal.blueprintId());
            companion.setMode(CompanionMode.FOLLOWING);
            reply(owner, data, "The blueprint is complete.");
            pending = null;
            return;
        }

        BlueprintProvider.Placement placement = pending.proposal.placements().get(pending.index);
        BlockPos position = pending.proposal.origin().offset(placement.relativePosition());
        if (!level.hasChunkAt(position)) {
            companion.getNavigation().moveTo(position.getX() + 0.5, position.getY(), position.getZ() + 0.5, 1.0);
            return;
        }
        if (companion.distanceToSqr(Vec3.atCenterOf(position)) > 30.25D) {
            companion.getNavigation().moveTo(position.getX() + 0.5, position.getY(), position.getZ() + 0.5, 1.0);
            return;
        }

        Block block = resolveBlock(placement.blockStateId());
        if (block == null) { pause(data, owner, "Unknown block " + placement.blockStateId()); return; }
        BlockState current = level.getBlockState(position);
        if (current.is(block)) { advance(data, level.getGameTime()); return; }
        if (!current.isAir() && !PlayerLikeActionService.breakBlock(companion, owner, position)) {
            pause(data, owner, "Cannot clear a protected or unreachable block at " + position.toShortString());
            return;
        }
        if (!level.getBlockState(position).isAir()) return;

        ItemStack material = findMaterial(owner, companion, block);
        if (material.isEmpty()) { pause(data, owner, "Missing material: " + BuiltInRegistries.BLOCK.getKey(block)); return; }
        BlockPos support = position.below();
        BlockHitResult hit = new BlockHitResult(Vec3.atCenterOf(support), Direction.UP, support, false);
        InteractionResult result = PlayerLikeActionService.placeBlock(companion, owner, position, hit, material);
        if (result.consumesAction() || level.getBlockState(position).is(block)) advance(data, level.getGameTime());
        else pause(data, owner, "Placement was refused at " + position.toShortString());
    }

    private static void acceptProposal(MinecraftServer server, BlueprintProvider provider,
                                       BlueprintProvider.BlueprintRequest request,
                                       BlueprintProvider.BlueprintProposal proposal, Throwable error) {
        CompanionSavedData data = CompanionSavedData.get(server);
        if (!request.requestId().equals(data.blueprintLedger().requestId())) return;
        ServerPlayer owner = server.getPlayerList().getPlayer(request.ownerUuid());
        ElvenCompanionEntity companion = CompanionSummonService.findLoaded(server, request.companionUuid());
        if (owner == null || companion == null) { pending = null; return; }
        if (error != null || proposal == null) {
            fail(data, owner, "Blueprint generation failed or timed out.");
            return;
        }
        Validation validation = validate(provider, proposal, owner, companion);
        if (!validation.valid) { fail(data, owner, "Blueprint rejected: " + validation.message); return; }
        pending = new Pending(provider, request, proposal, owner.getUUID());
        data.setBlueprintLedger(new BlueprintLedger(request.requestId(), proposal.blueprintId(),
                BlueprintLedger.State.PREVIEW, request.purpose(), proposal.integrityHash(),
                proposal.placements().size(), 0, validation.message, owner.level().getGameTime()));
        reply(owner, data, "Blueprint preview ready: " + proposal.placements().size() + " blocks, "
                + proposal.materials().size() + " material types. Say ‘" + data.companionName()
                + ", approve blueprint’ or ‘reject blueprint’. " + validation.message);
    }

    private static Validation validate(BlueprintProvider provider, BlueprintProvider.BlueprintProposal proposal,
                                       ServerPlayer owner, ElvenCompanionEntity companion) {
        if (proposal.blueprintId() == null || proposal.formatVersion() <= 0 || proposal.integrityHash().isBlank())
            return new Validation(false, "missing identity, format version, or integrity hash");
        if (proposal.placements().isEmpty() || proposal.placements().size() > MAX_PLACEMENTS)
            return new Validation(false, "placement count is outside 1–" + MAX_PLACEMENTS);
        BlueprintProvider.Bounds bounds = proposal.bounds();
        if (bounds == null || bounds.x() < 1 || bounds.y() < 1 || bounds.z() < 1
                || bounds.x() > MAX_BOUNDS.x() || bounds.y() > MAX_BOUNDS.y() || bounds.z() > MAX_BOUNDS.z())
            return new Validation(false, "bounds exceed the companion safety limit");
        if (!(companion.level() instanceof ServerLevel level) || owner.level() != level)
            return new Validation(false, "owner and companion are not together");

        List<BlueprintProvider.BlockSample> samples = new ArrayList<>();
        Set<Long> protectedPositions = new HashSet<>();
        for (BlueprintProvider.Placement placement : proposal.placements()) {
            BlockPos relative = placement.relativePosition();
            if (Math.abs(relative.getX()) >= bounds.x() || Math.abs(relative.getY()) >= bounds.y()
                    || Math.abs(relative.getZ()) >= bounds.z() || resolveBlock(placement.blockStateId()) == null)
                return new Validation(false, "proposal contains an invalid placement");
            BlockPos absolute = proposal.origin().offset(relative);
            samples.add(new BlueprintProvider.BlockSample(relative, level.getBlockState(absolute).toString()));
            if (!ClaimPermissionBridge.mayAct(owner, level, absolute, ClaimPermissionBridge.Action.PLACE))
                protectedPositions.add(absolute.asLong());
        }
        BlueprintProvider.BlueprintValidation result;
        try {
            result = provider.validate(proposal, new BlueprintProvider.BlueprintWorldSnapshot(
                    level.dimension().location().toString(), proposal.origin(), bounds, samples, protectedPositions));
        } catch (RuntimeException exception) {
            return new Validation(false, "provider validation failed");
        }
        if (result == null || !result.valid())
            return new Validation(false, result == null || result.errors().isEmpty()
                    ? "provider rejected the proposal" : String.join("; ", result.errors()));
        if (!protectedPositions.isEmpty()) return new Validation(false, "the site contains protected blocks");
        return new Validation(true, result.warnings().isEmpty() ? "No validation warnings."
                : String.join("; ", result.warnings()));
    }

    private static List<BlueprintProvider.MaterialAmount> materials(ServerPlayer owner,
                                                                    ElvenCompanionEntity companion) {
        Map<String, Integer> totals = new HashMap<>();
        for (ItemStack stack : owner.getInventory().items) addMaterial(totals, stack);
        for (int i = 0; i < companion.inventory().getContainerSize(); i++) addMaterial(totals, companion.inventory().getItem(i));
        return totals.entrySet().stream().sorted(Map.Entry.comparingByKey())
                .map(entry -> new BlueprintProvider.MaterialAmount(entry.getKey(), entry.getValue())).toList();
    }

    private static void addMaterial(Map<String, Integer> totals, ItemStack stack) {
        if (stack.isEmpty() || !(stack.getItem() instanceof BlockItem)) return;
        ResourceLocation id = BuiltInRegistries.ITEM.getKey(stack.getItem());
        totals.merge(id.toString(), stack.getCount(), Integer::sum);
    }

    private static ItemStack findMaterial(ServerPlayer owner, ElvenCompanionEntity companion, Block block) {
        for (int i = 0; i < companion.inventory().getContainerSize(); i++) {
            ItemStack stack = companion.inventory().getItem(i);
            if (stack.getItem() instanceof BlockItem item && item.getBlock() == block) return stack;
        }
        for (ItemStack stack : owner.getInventory().items) {
            if (stack.getItem() instanceof BlockItem item && item.getBlock() == block) return stack;
        }
        return ItemStack.EMPTY;
    }

    private static Block resolveBlock(String stateId) {
        if (stateId == null) return null;
        String idText = stateId.split("\\[", 2)[0].strip();
        ResourceLocation id = ResourceLocation.tryParse(idText);
        if (id == null || !BuiltInRegistries.BLOCK.containsKey(id)) return null;
        Block block = BuiltInRegistries.BLOCK.get(id);
        return block == net.minecraft.world.level.block.Blocks.AIR ? null : block;
    }

    private static void advance(CompanionSavedData data, long gameTime) {
        pending.index++;
        if (pending.index % 16 == 0 || pending.index == pending.proposal.placements().size())
            data.setBlueprintLedger(ledgerWith(data, BlueprintLedger.State.EXECUTING, pending.index, "Building", gameTime));
    }

    private static void pause(CompanionSavedData data, ServerPlayer owner, String message) {
        data.setBlueprintLedger(ledgerWith(data, BlueprintLedger.State.PAUSED, pending.index, message,
                owner.level().getGameTime()));
        reply(owner, data, message + ". The build is paused; ask for it again after resolving this.");
        pending = null;
    }

    private static void fail(CompanionSavedData data, ServerPlayer owner, String message) {
        data.setBlueprintLedger(ledgerWith(data, BlueprintLedger.State.FAILED, 0, message,
                owner.level().getGameTime()));
        data.setTask(ActiveTask.NONE, null);
        pending = null;
        reply(owner, data, message);
    }

    private static BlueprintLedger ledgerWith(CompanionSavedData data, BlueprintLedger.State state,
                                               int completed, String message, long gameTime) {
        BlueprintLedger old = data.blueprintLedger();
        return new BlueprintLedger(old.requestId(), old.blueprintId(), state, old.purpose(),
                old.integrityHash(), old.placementCount(), completed, message,
                gameTime);
    }

    private static void reply(ServerPlayer owner, CompanionSavedData data, String message) {
        owner.sendSystemMessage(Component.literal("§d[" + data.companionName() + "] §f" + message));
    }

    private static final class Pending {
        private final BlueprintProvider provider;
        private final BlueprintProvider.BlueprintRequest request;
        private final BlueprintProvider.BlueprintProposal proposal;
        private final UUID ownerUuid;
        private int index;

        private Pending(BlueprintProvider provider, BlueprintProvider.BlueprintRequest request,
                        BlueprintProvider.BlueprintProposal proposal, UUID ownerUuid) {
            this.provider = provider;
            this.request = request;
            this.proposal = proposal;
            this.ownerUuid = ownerUuid;
        }
    }

    private record Validation(boolean valid, String message) {}
}

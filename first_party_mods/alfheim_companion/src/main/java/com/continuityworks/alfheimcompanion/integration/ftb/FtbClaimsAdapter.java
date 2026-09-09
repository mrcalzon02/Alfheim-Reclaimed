package com.continuityworks.alfheimcompanion.integration.ftb;

import com.continuityworks.alfheimcompanion.integration.ClaimPermissionBridge;
import dev.ftb.mods.ftbchunks.api.ClaimedChunkManager;
import dev.ftb.mods.ftbchunks.api.FTBChunksAPI;
import dev.ftb.mods.ftbchunks.api.Protection;
import dev.ftb.mods.ftbchunks.api.ClaimResult;
import dev.ftb.mods.ftblibrary.math.ChunkDimPos;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.level.ChunkPos;

public final class FtbClaimsAdapter {
    private FtbClaimsAdapter() {}

    public static void register() {
        ClaimPermissionBridge.register((owner, level, position, action) -> {
            if (!FTBChunksAPI.api().isManagerLoaded()) return false;
            ClaimedChunkManager manager = FTBChunksAPI.api().getManager();
            Protection protection = switch (action) {
                case BREAK, PLACE -> Protection.EDIT_BLOCK;
                case INTERACT, CONTAINER_EXTRACT, CONTAINER_INSERT -> Protection.INTERACT_BLOCK;
            };
            return !manager.shouldPreventInteraction(owner, InteractionHand.MAIN_HAND,
                    position, protection, null);
        });
        ClaimPermissionBridge.registerClaimProvider((owner, level, chunk) -> {
            if (!FTBChunksAPI.api().isManagerLoaded())
                return new ClaimPermissionBridge.ClaimAttempt(false, "FTB Chunks is not ready.");
            ClaimedChunkManager manager = FTBChunksAPI.api().getManager();
            ChunkDimPos position = new ChunkDimPos(level.dimension(), new ChunkPos(chunk.x, chunk.z));
            if (manager.getChunk(position) != null)
                return new ClaimPermissionBridge.ClaimAttempt(false, "That chunk is already claimed.");
            ClaimResult result = manager.getOrCreateData(owner).claim(owner.createCommandSourceStack(),
                    position, false);
            return new ClaimPermissionBridge.ClaimAttempt(result.isSuccess(), result.getMessage().getString());
        });
        ClaimPermissionBridge.registerClaimStatusProvider((level, chunk) -> {
            if (!FTBChunksAPI.api().isManagerLoaded()) return true;
            return FTBChunksAPI.api().getManager().getChunk(
                    new ChunkDimPos(level.dimension(), new ChunkPos(chunk.x, chunk.z))) != null;
        });
        ClaimPermissionBridge.registerClaimMutationProvider(new ClaimPermissionBridge.ClaimMutationProvider() {
            @Override
            public ClaimPermissionBridge.ClaimAttempt previewClaim(net.minecraft.server.level.ServerPlayer owner,
                                                                   net.minecraft.server.level.ServerLevel level,
                                                                   ChunkPos chunk) {
                if (!FTBChunksAPI.api().isManagerLoaded())
                    return new ClaimPermissionBridge.ClaimAttempt(false, "FTB Chunks is not ready.");
                ChunkDimPos position = new ChunkDimPos(level.dimension(), chunk);
                ClaimResult result = FTBChunksAPI.api().getManager().getOrCreateData(owner)
                        .claim(owner.createCommandSourceStack(), position, true);
                return new ClaimPermissionBridge.ClaimAttempt(result.isSuccess(), result.getMessage().getString());
            }

            @Override
            public ClaimPermissionBridge.ClaimAttempt unclaim(net.minecraft.server.level.ServerPlayer owner,
                                                              net.minecraft.server.level.ServerLevel level,
                                                              ChunkPos chunk) {
                if (!FTBChunksAPI.api().isManagerLoaded())
                    return new ClaimPermissionBridge.ClaimAttempt(false, "FTB Chunks is not ready.");
                ChunkDimPos position = new ChunkDimPos(level.dimension(), chunk);
                ClaimResult result = FTBChunksAPI.api().getManager().getOrCreateData(owner)
                        .unclaim(owner.createCommandSourceStack(), position, false);
                return new ClaimPermissionBridge.ClaimAttempt(result.isSuccess(), result.getMessage().getString());
            }
        });
    }
}

package com.continuityworks.alfheimcompanion.integration.ftb;

import com.continuityworks.alfheimcompanion.integration.ClaimPermissionBridge;
import dev.ftb.mods.ftbchunks.api.ClaimedChunkManager;
import dev.ftb.mods.ftbchunks.api.FTBChunksAPI;
import dev.ftb.mods.ftbchunks.api.Protection;
import net.minecraft.world.InteractionHand;

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
    }
}

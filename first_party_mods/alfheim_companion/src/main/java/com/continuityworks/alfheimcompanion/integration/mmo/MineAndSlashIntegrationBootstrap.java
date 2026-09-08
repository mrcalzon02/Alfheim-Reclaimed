package com.continuityworks.alfheimcompanion.integration.mmo;

import com.continuityworks.alfheimcompanion.AlfheimCompanion;
import com.continuityworks.alfheimcompanion.integration.CombatProfileBridge;
import net.minecraftforge.fml.ModList;

/** Keeps Mine and Slash classes completely cold when that optional mod is absent. */
public final class MineAndSlashIntegrationBootstrap {
    private MineAndSlashIntegrationBootstrap() {}

    public static void registerIfAvailable() {
        if (!ModList.get().isLoaded("mmorpg")) {
            AlfheimCompanion.LOGGER.info("Mine and Slash integration unavailable; using Forge combat only");
            return;
        }
        CombatProfileBridge.register(new MineAndSlashCombatProfileProvider());
        AlfheimCompanion.LOGGER.info("Mine and Slash 6.4.x combat integration connected");
    }
}

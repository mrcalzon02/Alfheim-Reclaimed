package com.continuityworks.alfheimcompanion.integration.ftb;

import com.continuityworks.alfheimcompanion.AlfheimCompanion;
import net.minecraftforge.fml.ModList;

public final class FtbIntegrationBootstrap {
    private FtbIntegrationBootstrap() {}

    public static void registerAvailableAdapters() {
        if (ModList.get().isLoaded("ftbchunks")) {
            FtbClaimsAdapter.register();
            AlfheimCompanion.LOGGER.info("FTB Chunks claims adapter connected");
        }
        if (ModList.get().isLoaded("ftbquests")) {
            FtbQuestAdapter.register();
            AlfheimCompanion.LOGGER.info("FTB Quests awareness adapter connected");
        }
    }
}

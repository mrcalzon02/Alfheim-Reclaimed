package com.continuityworks.alfheimcompanion.brain;

import com.continuityworks.alfheimcompanion.AlfheimCompanion;
import com.continuityworks.alfheimcompanion.brain.local.InferenceSettings;
import com.continuityworks.alfheimcompanion.brain.local.LocalJlamaTinyBrainEngine;
import com.continuityworks.alfheimcompanion.brain.local.ResilientTinyBrainEngine;
import net.minecraftforge.fml.loading.FMLPaths;

import java.io.IOException;

public final class InferenceBootstrap {
    private InferenceBootstrap() {}

    public static void installConfiguredEngine() {
        try {
            InferenceSettings settings = InferenceSettings.load(FMLPaths.CONFIGDIR.get(), FMLPaths.GAMEDIR.get());
            if (!settings.enabled()) {
                AlfheimCompanion.LOGGER.info("Local companion inference is disabled; deterministic responses remain active");
                return;
            }
            CompanionBrainCoordinator.installEngine(new ResilientTinyBrainEngine(
                    new LocalJlamaTinyBrainEngine(settings), new RuleBasedTinyBrainEngine()));
        } catch (IOException | IllegalArgumentException error) {
            AlfheimCompanion.LOGGER.error("Invalid local companion inference configuration; using deterministic responses",
                    error);
        }
    }
}

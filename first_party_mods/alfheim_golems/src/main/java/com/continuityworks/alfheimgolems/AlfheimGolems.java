package com.continuityworks.alfheimgolems;

import com.continuityworks.alfheimgolems.command.GolemDiagnosticsCommand;
import com.continuityworks.alfheimgolems.config.GolemConfig;
import com.mojang.logging.LogUtils;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.fml.ModLoadingContext;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.config.ModConfig;
import org.slf4j.Logger;

/**
 * Server-safe foundation for Alfheim Golems.
 *
 * <p>G0 registers no entities or items. Later slices build on the bounded order, persistence and
 * diagnostics contracts without importing Alfheim Companion's singleton or inference lifecycle.
 */
@Mod(AlfheimGolems.MOD_ID)
public final class AlfheimGolems {
    public static final String MOD_ID = "alfheim_golems";
    public static final Logger LOGGER = LogUtils.getLogger();

    public AlfheimGolems() {
        ModLoadingContext.get().registerConfig(ModConfig.Type.COMMON, GolemConfig.SPEC);
        MinecraftForge.EVENT_BUS.addListener(this::registerCommands);
    }

    private void registerCommands(RegisterCommandsEvent event) {
        GolemDiagnosticsCommand.register(event.getDispatcher());
    }
}

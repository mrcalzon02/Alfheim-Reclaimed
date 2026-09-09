package com.continuityworks.alfheimgolems.command;

import com.continuityworks.alfheimgolems.data.GolemNetworkSavedData;
import com.continuityworks.alfheimgolems.diagnostic.GolemDiagnostics;
import com.mojang.brigadier.CommandDispatcher;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;

/** Operator-only, read-only diagnostics for automated runtime gates. */
public final class GolemDiagnosticsCommand {
    private GolemDiagnosticsCommand() {}

    public static void register(CommandDispatcher<CommandSourceStack> dispatcher) {
        dispatcher.register(Commands.literal("alfheimgolems")
                .requires(source -> source.hasPermission(2))
                .then(Commands.literal("debug")
                        .then(Commands.literal("summary").executes(context -> {
                            GolemNetworkSavedData data = GolemNetworkSavedData.get(
                                    context.getSource().getServer());
                            String message = GolemDiagnostics.snapshot().summary()
                                    + " data_version=" + data.loadedDataVersion()
                                    + " read_only=" + data.readOnly();
                            context.getSource().sendSuccess(() -> Component.literal(message), false);
                            return 1;
                        }))));
    }
}

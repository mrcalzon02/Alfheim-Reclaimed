package com.continuityworks.alfheimcompanion.command;

import com.continuityworks.alfheimcompanion.entity.ElvenCompanionEntity;
import com.continuityworks.alfheimcompanion.memory.CompanionSavedData;
import com.continuityworks.alfheimcompanion.memory.PlayerCompanionBinding;
import com.continuityworks.alfheimcompanion.personality.ElvenNames;
import com.continuityworks.alfheimcompanion.service.CompanionSummonService;
import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.StringArgumentType;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.SharedSuggestionProvider;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;

public final class CompanionAdminCommands {
    private CompanionAdminCommands() {}

    public static void register(CommandDispatcher<CommandSourceStack> dispatcher) {
        dispatcher.register(Commands.literal("alfheimcompanion")
                .then(Commands.literal("profile")
                        .then(Commands.literal("list").executes(context -> listProfiles(context.getSource())))
                        .then(Commands.literal("set").then(Commands.argument("name", StringArgumentType.word())
                                .suggests((context, builder) -> SharedSuggestionProvider.suggest(ElvenNames.all(), builder))
                                .executes(context -> setProfile(context.getSource(), StringArgumentType.getString(context, "name"))))))
                .then(Commands.literal("outfit")
                        .then(Commands.literal("list").executes(context -> listOutfits(context.getSource())))
                        .then(Commands.literal("set").then(Commands.argument("outfit", StringArgumentType.word())
                                .suggests((context, builder) -> SharedSuggestionProvider.suggest(CompanionSavedData.OUTFITS, builder))
                                .executes(context -> setOutfit(context.getSource(), StringArgumentType.getString(context, "outfit"))))))
                .then(Commands.literal("reset").executes(context -> reset(context.getSource()))));
    }

    private static int listProfiles(CommandSourceStack source) {
        source.sendSuccess(() -> Component.literal("Companion profiles: " + String.join(", ", ElvenNames.all())), false);
        return 1;
    }

    private static int listOutfits(CommandSourceStack source) {
        source.sendSuccess(() -> Component.literal("Companion outfits: " + String.join(", ", CompanionSavedData.OUTFITS)), false);
        return 1;
    }

    private static int setProfile(CommandSourceStack source, String name) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
        ServerPlayer player = source.getPlayerOrException();
        CompanionSavedData data = CompanionSavedData.get(player.server);
        if (!data.setPlayerProfile(player.getUUID(), name, player.server.overworld().getGameTime())) {
            source.sendFailure(Component.literal("Unknown profile. Use /alfheimcompanion profile list."));
            return 0;
        }
        refreshVisibleName(player, data);
        source.sendSuccess(() -> Component.literal("Your companion profile is now " + name + "."), false);
        return 1;
    }

    private static int setOutfit(CommandSourceStack source, String outfit) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
        ServerPlayer player = source.getPlayerOrException();
        CompanionSavedData data = CompanionSavedData.get(player.server);
        if (!data.setPlayerOutfit(player.getUUID(), outfit, player.server.overworld().getGameTime())) {
            source.sendFailure(Component.literal("Unknown outfit. Use /alfheimcompanion outfit list."));
            return 0;
        }
        source.sendSuccess(() -> Component.literal("Your companion outfit is now " + outfit + "."), false);
        return 1;
    }

    private static int reset(CommandSourceStack source) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
        ServerPlayer player = source.getPlayerOrException();
        CompanionSavedData data = CompanionSavedData.get(player.server);
        PlayerCompanionBinding old = data.playerBinding(player.getUUID()).orElse(null);
        if (old != null && old.alive()) {
            source.sendFailure(Component.literal("Reset is available only after your bound companion has fallen."));
            return 0;
        }
        PlayerCompanionBinding fresh = data.resetPlayerBinding(player.getUUID(),
                player.server.overworld().getGameTime() ^ player.getUUID().hashCode());
        source.sendSuccess(() -> Component.literal("A new binding awaits: " + fresh.name()
                + " in the " + fresh.outfit() + " outfit."), false);
        return 1;
    }

    private static void refreshVisibleName(ServerPlayer player, CompanionSavedData data) {
        if (!data.ownerUuid().filter(player.getUUID()::equals).isPresent()) return;
        ElvenCompanionEntity companion = CompanionSummonService.findLoaded(player.server,
                data.companionUuid().orElse(null));
        if (companion != null) companion.setCustomName(Component.literal(data.companionName()));
    }
}

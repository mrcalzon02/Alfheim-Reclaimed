package com.continuityworks.alfheimcompanion.command;

import com.continuityworks.alfheimcompanion.api.quest.QuestProvider;
import com.continuityworks.alfheimcompanion.brain.CompanionBrainCoordinator;
import com.continuityworks.alfheimcompanion.entity.ElvenCompanionEntity;
import com.continuityworks.alfheimcompanion.integration.ContinuityWorksBridge;
import com.continuityworks.alfheimcompanion.integration.QuestAwarenessBridge;
import com.continuityworks.alfheimcompanion.memory.CompanionMode;
import com.continuityworks.alfheimcompanion.memory.CompanionSavedData;
import com.continuityworks.alfheimcompanion.memory.MemoryEntry;
import com.continuityworks.alfheimcompanion.personality.DialogueBank;
import com.continuityworks.alfheimcompanion.service.CompanionSummonService;
import com.continuityworks.alfheimcompanion.service.CraftingAdvisor;
import com.continuityworks.alfheimcompanion.service.ItemTaskService;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;

import java.util.Locale;
import java.util.Optional;

public final class CompanionCommandService {
    private CompanionCommandService() {}

    public static boolean handle(ServerPlayer player, String rawMessage) {
        CompanionSavedData data = CompanionSavedData.get(player.server);
        Optional<AddressedCommandParser.Parsed> parsed = AddressedCommandParser.parse(
                data.companionName(), rawMessage);
        if (parsed.isEmpty()) return false;

        ElvenCompanionEntity companion = CompanionSummonService.findLoaded(player.server,
                data.companionUuid().orElse(null));
        if (companion == null || companion.ownerUuid() == null
                || !companion.ownerUuid().equals(player.getUUID())) return false;

        AddressedCommandParser.Parsed command = parsed.get();
        switch (command.verb()) {
            case FOLLOW -> {
                data.setTask("", null);
                companion.setMode(CompanionMode.FOLLOWING);
                reply(player, data, DialogueBank.line(DialogueBank.Moment.FOLLOW, player.level().getGameTime()));
            }
            case GUARD -> {
                data.setTask("guard", null);
                data.rememberFact("guard_anchor", companion.level().dimension().location() + "@" + companion.blockPosition().asLong());
                companion.setGuardPosition(companion.blockPosition());
                companion.setMode(CompanionMode.GUARDING);
                reply(player, data, DialogueBank.line(DialogueBank.Moment.WAIT, player.level().getGameTime()));
            }
            case CANCEL -> {
                data.setTask("", null);
                companion.setMode(CompanionMode.FOLLOWING);
                reply(player, data, "I have set the task aside.");
            }
            case STATUS -> reply(player, data, data.activeTask().isBlank()
                    ? "I have no unfinished task." : "My current task is " + data.activeTask() + ".");
            case QUEST -> describeQuest(player, data, command.target());
            case BUILD -> {
                String task = "build|" + safe(command.target());
                data.setTask(task, null);
                rememberRequest(player, data, task);
                if (ContinuityWorksBridge.provider().isEmpty()) {
                    reply(player, data, "I can plan that, but the Continuity Works blueprint endpoint is not connected yet.");
                } else {
                    CompanionBrainCoordinator.requestComplexPlan(player.server);
                    reply(player, data, "I will study the site and prepare a blueprint proposal.");
                }
            }
            case CRAFT -> {
                String task = "craft|" + command.count() + "|" + safe(command.target());
                data.setTask(task, null);
                rememberRequest(player, data, task);
                reply(player, data, CraftingAdvisor.describe(player, companion, command.target(), command.count()));
            }
            case SHOW_ITEM, FETCH_ITEM, LEAD_TO_ITEM -> {
                String approach = switch (command.verb()) {
                    case SHOW_ITEM -> "show";
                    case FETCH_ITEM -> "fetch";
                    default -> "lead";
                };
                String task = "item|" + approach + "|" + command.count() + "|" + safe(command.target());
                data.setTask(task, null);
                rememberRequest(player, data, task);
                ItemTaskService.Approach itemApproach = switch (approach) {
                    case "show" -> ItemTaskService.Approach.SHOW;
                    case "fetch" -> ItemTaskService.Approach.FETCH;
                    default -> ItemTaskService.Approach.LEAD;
                };
                ItemTaskService.StartResult start = ItemTaskService.start(player, companion,
                        command.target(), command.count(), itemApproach);
                if (!start.started()) data.setTask("", null);
                reply(player, data, start.message());
            }
        }
        return true;
    }

    private static void describeQuest(ServerPlayer player, CompanionSavedData data, String query) {
        Optional<QuestProvider> provider = QuestAwarenessBridge.provider();
        if (provider.isEmpty()) {
            reply(player, data, "I cannot read the quest ledger until its adapter is connected.");
            return;
        }
        String needle = query.toLowerCase(Locale.ROOT);
        provider.get().questsFor(player).stream()
                .filter(quest -> quest.id().toLowerCase(Locale.ROOT).contains(needle)
                        || quest.name().toLowerCase(Locale.ROOT).contains(needle)
                        || quest.goal().toLowerCase(Locale.ROOT).contains(needle)
                        || quest.ingredients().stream().anyMatch(i -> i.itemOrTagId().toLowerCase(Locale.ROOT).contains(needle))
                        || quest.criteria().stream().anyMatch(c -> c.toLowerCase(Locale.ROOT).contains(needle)))
                .findFirst()
                .ifPresentOrElse(quest -> {
                    data.rememberFact("quest:" + quest.id(), quest.status().name());
                    reply(player, data, quest.name() + " is " + quest.status().name().toLowerCase(Locale.ROOT)
                            + ". " + quest.goal());
                }, () -> reply(player, data, "I found no quest matching " + query + "."));
    }

    private static void rememberRequest(ServerPlayer player, CompanionSavedData data, String task) {
        data.remember(new MemoryEntry(player.level().getGameTime(), "request", player.getName().getString(), task, 6));
    }

    private static void reply(ServerPlayer player, CompanionSavedData data, String message) {
        player.sendSystemMessage(Component.literal("§d[" + data.companionName() + "] §f" + message));
    }

    private static String safe(String value) {
        return value.replace('|', ' ').strip().substring(0, Math.min(64, value.replace('|', ' ').strip().length()));
    }
}

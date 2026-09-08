package com.continuityworks.alfheimcompanion.command;

import com.continuityworks.alfheimcompanion.api.quest.QuestProvider;
import com.continuityworks.alfheimcompanion.brain.CompanionBrainCoordinator;
import com.continuityworks.alfheimcompanion.entity.ElvenCompanionEntity;
import com.continuityworks.alfheimcompanion.integration.ContinuityWorksBridge;
import com.continuityworks.alfheimcompanion.integration.QuestAwarenessBridge;
import com.continuityworks.alfheimcompanion.memory.CompanionMode;
import com.continuityworks.alfheimcompanion.memory.ActiveTask;
import com.continuityworks.alfheimcompanion.memory.CompanionSavedData;
import com.continuityworks.alfheimcompanion.memory.MemoryEntry;
import com.continuityworks.alfheimcompanion.personality.DialogueBank;
import com.continuityworks.alfheimcompanion.service.CompanionSummonService;
import com.continuityworks.alfheimcompanion.service.CraftingAdvisor;
import com.continuityworks.alfheimcompanion.service.ItemTaskService;
import com.continuityworks.alfheimcompanion.service.BlueprintLifecycleService;
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
        long leaseTime = player.server.overworld().getGameTime();
        if (!data.leaseHeldBy(player.getUUID(), leaseTime)) {
            reply(player, data, "My lease is available. Use the sigil to summon me before giving a task.");
            return true;
        }
        data.claimOrRefreshLease(player.getUUID(), leaseTime);

        AddressedCommandParser.Parsed command = parsed.get();
        switch (command.verb()) {
            case FOLLOW -> {
                data.setTask(new ActiveTask(ActiveTask.Kind.FOLLOW, "", "", 1,
                        player.level().getGameTime()), null);
                companion.setMode(CompanionMode.FOLLOWING);
                reply(player, data, DialogueBank.line(DialogueBank.Moment.FOLLOW,
                        player.level().getGameTime(), data.companionName(), data.moodIndex()));
            }
            case GUARD -> {
                data.setTask(new ActiveTask(ActiveTask.Kind.GUARD, "", "", 1,
                        player.level().getGameTime()), null);
                data.rememberFact("guard_anchor", companion.level().dimension().location() + "@" + companion.blockPosition().asLong());
                companion.setGuardPosition(companion.blockPosition());
                companion.setMode(CompanionMode.GUARDING);
                reply(player, data, DialogueBank.line(DialogueBank.Moment.WAIT,
                        player.level().getGameTime(), data.companionName(), data.moodIndex()));
            }
            case CANCEL -> {
                BlueprintLifecycleService.cancel(player.server);
                data.setTask(ActiveTask.NONE, null);
                companion.setMode(CompanionMode.FOLLOWING);
                reply(player, data, "I have set the task aside.");
            }
            case STATUS -> reply(player, data, data.activeTask().isBlank()
                    ? "I have no unfinished task. Blueprint state: " + data.blueprintLedger().state().name().toLowerCase(Locale.ROOT)
                    + ". Nutrition " + companion.nutrition() + "/20, stamina " + companion.stamina()
                    + "/100, mood " + data.moodIndex() + "."
                    : "My current task is " + data.activeTask() + ". Blueprint state: "
                    + data.blueprintLedger().state().name().toLowerCase(Locale.ROOT)
                    + ". Nutrition " + companion.nutrition() + "/20, stamina " + companion.stamina()
                    + "/100, mood " + data.moodIndex() + ".");
            case APPROVE_BLUEPRINT -> BlueprintLifecycleService.approve(player, companion);
            case REJECT_BLUEPRINT -> BlueprintLifecycleService.reject(player);
            case DEFEND -> {
                companion.setMode(CompanionMode.DEFENDING);
                reply(player, data, DialogueBank.line(DialogueBank.Moment.DEFEND,
                        player.level().getGameTime(), data.companionName(), data.moodIndex()));
            }
            case RETREAT -> {
                companion.setTarget(null);
                companion.setMode(CompanionMode.RETREATING);
                reply(player, data, DialogueBank.line(DialogueBank.Moment.RETREAT,
                        player.level().getGameTime(), data.companionName(), data.moodIndex()));
            }
            case QUEST -> describeQuest(player, data, command.target());
            case BUILD -> {
                String task = "build|" + safe(command.target());
                data.setTask(new ActiveTask(ActiveTask.Kind.BUILD, "", command.target(), 1,
                        player.level().getGameTime()), null);
                rememberRequest(player, data, task);
                if (ContinuityWorksBridge.provider().isEmpty()) {
                    reply(player, data, "I can plan that, but the Continuity Works blueprint endpoint is not connected yet.");
                } else {
                    CompanionBrainCoordinator.requestComplexPlan(player.server);
                    BlueprintLifecycleService.request(player, companion, command.target());
                    reply(player, data, "I will study the site and prepare a bounded blueprint proposal.");
                }
            }
            case CRAFT -> {
                String task = "craft|" + command.count() + "|" + safe(command.target());
                data.setTask(new ActiveTask(ActiveTask.Kind.CRAFT, "", command.target(), command.count(),
                        player.level().getGameTime()), null);
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
                data.setTask(new ActiveTask(ActiveTask.Kind.ITEM, approach, command.target(), command.count(),
                        player.level().getGameTime()), null);
                rememberRequest(player, data, task);
                ItemTaskService.Approach itemApproach = switch (approach) {
                    case "show" -> ItemTaskService.Approach.SHOW;
                    case "fetch" -> ItemTaskService.Approach.FETCH;
                    default -> ItemTaskService.Approach.LEAD;
                };
                ItemTaskService.StartResult start = ItemTaskService.start(player, companion,
                        command.target(), command.count(), itemApproach);
                if (!start.started()) data.setTask(ActiveTask.NONE, null);
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

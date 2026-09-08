package com.continuityworks.alfheimcompanion.service;

import com.continuityworks.alfheimcompanion.entity.ElvenCompanionEntity;
import com.continuityworks.alfheimcompanion.integration.CombatProfileBridge;
import com.continuityworks.alfheimcompanion.memory.ActiveTask;
import com.continuityworks.alfheimcompanion.memory.CompanionMode;
import com.continuityworks.alfheimcompanion.memory.CompanionSavedData;
import com.continuityworks.alfheimcompanion.network.WheelAction;
import com.continuityworks.alfheimcompanion.registry.ModItems;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;

/** Server authority for the radial UI. The packet carries an enum, never command text. */
public final class WheelActionService {
    private static final java.util.Map<java.util.UUID, Integer> LAST_ACTION_TICK = new java.util.HashMap<>();
    private WheelActionService() {}

    public static void execute(ServerPlayer player, WheelAction action) {
        int nowTick = player.server.getTickCount();
        int lastTick = LAST_ACTION_TICK.getOrDefault(player.getUUID(), Integer.MIN_VALUE / 2);
        if (nowTick - lastTick < 4) return;
        LAST_ACTION_TICK.put(player.getUUID(), nowTick);
        if (!ownsSigil(player)) {
            player.sendSystemMessage(Component.literal("The command wheel requires the Sigil of the Hollow Court."));
            return;
        }
        if (action == WheelAction.SUMMON_RECALL) {
            CompanionSummonService.summonOrRecall(player);
            return;
        }

        CompanionSavedData data = CompanionSavedData.get(player.server);
        long now = player.server.overworld().getGameTime();
        if (data.leaseHeldByOther(player.getUUID(), now)) {
            player.sendSystemMessage(Component.literal("§d[" + data.companionName()
                    + "] §fSorry, I’m currently busy!"));
            return;
        }
        if (!data.leaseHeldBy(player.getUUID(), now)) {
            reply(player, data, "My lease is available. Choose Summon / Recall first.");
            return;
        }
        data.claimOrRefreshLease(player.getUUID(), now);
        if (action == WheelAction.DISMISS) {
            CompanionSummonService.dismiss(player);
            return;
        }
        ElvenCompanionEntity companion = CompanionSummonService.findLoaded(player.server,
                data.companionUuid().orElse(null));
        if (companion == null || !player.getUUID().equals(companion.ownerUuid())) {
            reply(player, data, "I am not presently summoned.");
            return;
        }

        switch (action) {
            case FOLLOW -> {
                data.setTask(new ActiveTask(ActiveTask.Kind.FOLLOW, "", "", 1,
                        player.level().getGameTime()), null);
                companion.setMode(CompanionMode.FOLLOWING);
                reply(player, data, "I will follow.");
            }
            case WAIT -> {
                companion.getNavigation().stop();
                companion.setMode(CompanionMode.WAITING);
                reply(player, data, "I will wait here.");
            }
            case GUARD -> {
                data.setTask(new ActiveTask(ActiveTask.Kind.GUARD, "", "", 1,
                        player.level().getGameTime()), null);
                data.rememberFact("guard_anchor", companion.level().dimension().location()
                        + "@" + companion.blockPosition().asLong());
                companion.setGuardPosition(companion.blockPosition());
                companion.setMode(CompanionMode.GUARDING);
                reply(player, data, "I will guard this place.");
            }
            case STATUS -> reply(player, data, data.activeTask().isBlank()
                    ? "No unfinished task. Blueprint: " + data.blueprintLedger().state().name().toLowerCase()
                    + ". Nutrition " + companion.nutrition() + "/20, stamina " + companion.stamina()
                    + "/100, mood " + data.moodIndex() + "."
                    + CombatProfileBridge.statusSuffix(player, companion)
                    : "Current task: " + data.activeTask() + ". Blueprint: "
                    + data.blueprintLedger().state().name().toLowerCase()
                    + ". Nutrition " + companion.nutrition() + "/20, stamina " + companion.stamina()
                    + "/100, mood " + data.moodIndex() + "."
                    + CombatProfileBridge.statusSuffix(player, companion));
            case CANCEL_TASK -> {
                BlueprintLifecycleService.cancel(player.server);
                data.setTask(ActiveTask.NONE, null);
                companion.setMode(CompanionMode.FOLLOWING);
                reply(player, data, "I have set the task aside.");
            }
            case DEFEND -> {
                companion.setMode(CompanionMode.DEFENDING);
                reply(player, data, "Stay close. I will defend you.");
            }
            case SUMMON_RECALL, DISMISS -> { }
        }
    }

    public static void clearRateLimits() { LAST_ACTION_TICK.clear(); }

    private static boolean ownsSigil(ServerPlayer player) {
        ItemStack sigil = new ItemStack(ModItems.COMPANION_SIGIL.get());
        return player.getInventory().contains(sigil);
    }

    private static void reply(ServerPlayer player, CompanionSavedData data, String message) {
        player.sendSystemMessage(Component.literal("§d[" + data.companionName() + "] §f" + message));
    }
}

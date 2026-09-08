package com.continuityworks.alfheimcompanion.integration.ftb;

import com.continuityworks.alfheimcompanion.api.quest.QuestProvider;
import com.continuityworks.alfheimcompanion.integration.QuestAwarenessBridge;
import dev.ftb.mods.ftbquests.api.FTBQuestsAPI;
import dev.ftb.mods.ftbquests.quest.BaseQuestFile;
import dev.ftb.mods.ftbquests.quest.Quest;
import dev.ftb.mods.ftbquests.quest.TeamData;
import dev.ftb.mods.ftbquests.quest.task.ItemTask;
import dev.ftb.mods.ftbquests.quest.task.Task;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.ArrayList;
import java.util.List;

public final class FtbQuestAdapter implements QuestProvider {
    private FtbQuestAdapter() {}

    public static void register() {
        QuestAwarenessBridge.register(new FtbQuestAdapter());
    }

    @Override
    public int apiVersion() {
        return API_VERSION;
    }

    @Override
    public List<QuestView> questsFor(ServerPlayer player) {
        BaseQuestFile file = FTBQuestsAPI.api().getQuestFile(true);
        if (file == null) return List.of();
        TeamData teamData = file.getOrCreateTeamData(player);
        List<QuestView> views = new ArrayList<>();
        file.forAllQuests(quest -> views.add(view(player, teamData, quest)));
        return List.copyOf(views);
    }

    private static QuestView view(ServerPlayer player, TeamData teamData, Quest quest) {
        Status status;
        if (teamData.isCompleted(quest)) status = Status.COMPLETED;
        else if (!quest.isVisible(teamData) || !teamData.areDependenciesVisible(quest)) status = Status.NOT_AVAILABLE;
        else if (teamData.isStarted(quest)) status = Status.ACTIVE;
        else status = Status.AVAILABLE;

        String goal = quest.getDescription().stream().map(Component::getString)
                .filter(text -> !text.isBlank()).findFirst().orElseGet(() -> quest.getSubtitle().getString());
        List<ObjectiveView> objectives = new ArrayList<>();
        List<IngredientView> ingredients = new ArrayList<>();
        List<String> criteria = new ArrayList<>();
        for (Task task : quest.getTasks()) {
            int current = saturated(teamData.getProgress(task));
            int required = saturated(task.getMaxProgress());
            String description = task.getTitle().getString();
            objectives.add(new ObjectiveView(task.getCodeString(), description, current, required,
                    teamData.isCompleted(task)));
            if (task instanceof ItemTask itemTask) {
                ItemStack sample = itemTask.getItemStack();
                String id = String.valueOf(ForgeRegistries.ITEMS.getKey(sample.getItem()));
                ingredients.add(new IngredientView(id, required, inventoryCount(player, sample.getItem())));
            } else if (!description.isBlank()) {
                criteria.add(description);
            }
        }
        return new QuestView(quest.getCodeString(), quest.getTitle().getString(), goal, status,
                objectives, ingredients, criteria);
    }

    private static int inventoryCount(ServerPlayer player, Item item) {
        int total = 0;
        for (ItemStack stack : player.getInventory().items) if (stack.is(item)) total += stack.getCount();
        return total;
    }

    private static int saturated(long value) {
        return (int) Math.max(0L, Math.min(Integer.MAX_VALUE, value));
    }
}

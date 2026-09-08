package com.continuityworks.alfheimcompanion.memory;

import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;

import java.util.ArrayDeque;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import com.continuityworks.alfheimcompanion.personality.ElvenNames;

public final class CompanionSavedData extends SavedData {
    private static final String DATA_NAME = "alfheim_companion_state";
    private static final int DATA_VERSION = 1;
    private static final int MAX_EPISODES = 50;
    private static final int MAX_FACTS = 64;

    private UUID companionUuid;
    private UUID ownerUuid;
    private String companionName = "";
    private String dimensionId = "minecraft:overworld";
    private BlockPos lastPosition = BlockPos.ZERO;
    private CompanionMode mode = CompanionMode.DISMISSED;
    private long latestRequestId;
    private UUID activeBlueprintId;
    private String activeTask = "";
    private int agitation;
    private long lastSummonGameTime = Long.MIN_VALUE;
    private long lastAgitationUpdate;
    private final ArrayDeque<MemoryEntry> episodes = new ArrayDeque<>();
    private final LinkedHashMap<String, String> facts = new LinkedHashMap<>();

    public static CompanionSavedData get(MinecraftServer server) {
        return server.overworld().getDataStorage().computeIfAbsent(
                CompanionSavedData::load, CompanionSavedData::new, DATA_NAME);
    }

    public Optional<UUID> companionUuid() { return Optional.ofNullable(companionUuid); }
    public Optional<UUID> ownerUuid() { return Optional.ofNullable(ownerUuid); }
    public String companionName() { return companionName.isBlank() ? "Companion" : companionName; }
    public String dimensionId() { return dimensionId; }
    public BlockPos lastPosition() { return lastPosition; }
    public CompanionMode mode() { return mode; }
    public long latestRequestId() { return latestRequestId; }
    public Optional<UUID> activeBlueprintId() { return Optional.ofNullable(activeBlueprintId); }
    public String activeTask() { return activeTask; }
    public int agitation(long gameTime) {
        decayAgitation(gameTime);
        return agitation;
    }
    public List<MemoryEntry> episodes() { return List.copyOf(episodes); }
    public Map<String, String> facts() { return Collections.unmodifiableMap(facts); }

    public void bind(UUID companionUuid, UUID ownerUuid, String dimensionId, BlockPos position) {
        if (this.companionName.isBlank()) this.companionName = ElvenNames.select(companionUuid);
        this.companionUuid = companionUuid;
        this.ownerUuid = ownerUuid;
        this.dimensionId = dimensionId;
        this.lastPosition = position.immutable();
        this.mode = CompanionMode.FOLLOWING;
        setDirty();
    }

    public void updateLocation(String dimensionId, BlockPos position) {
        this.dimensionId = dimensionId;
        this.lastPosition = position.immutable();
        setDirty();
    }

    public void setMode(CompanionMode mode) {
        this.mode = mode;
        setDirty();
    }

    public long nextRequestId() {
        latestRequestId++;
        setDirty();
        return latestRequestId;
    }

    public int recordSummon(long gameTime) {
        decayAgitation(gameTime);
        if (lastSummonGameTime != Long.MIN_VALUE) {
            long elapsed = Math.max(0, gameTime - lastSummonGameTime);
            if (elapsed < 100) agitation = Math.min(10, agitation + 2);
            else if (elapsed < 400) agitation = Math.min(10, agitation + 1);
        }
        lastSummonGameTime = gameTime;
        lastAgitationUpdate = gameTime;
        setDirty();
        return agitation;
    }

    public void setTask(String task, UUID blueprintId) {
        this.activeTask = task == null ? "" : task.substring(0, Math.min(task.length(), 96));
        this.activeBlueprintId = blueprintId;
        setDirty();
    }

    public void remember(MemoryEntry memory) {
        episodes.addLast(memory);
        while (episodes.size() > MAX_EPISODES) episodes.removeFirst();
        setDirty();
    }

    public void rememberFact(String key, String value) {
        String safeKey = limit(key, 64);
        if (!facts.containsKey(safeKey) && facts.size() >= MAX_FACTS) {
            facts.remove(facts.keySet().iterator().next());
        }
        facts.put(safeKey, limit(value, 160));
        setDirty();
    }

    public void dismiss() {
        mode = CompanionMode.DISMISSED;
        activeTask = "";
        activeBlueprintId = null;
        setDirty();
    }

    @Override
    public CompoundTag save(CompoundTag tag) {
        tag.putInt("version", DATA_VERSION);
        if (companionUuid != null) tag.putUUID("companion", companionUuid);
        if (ownerUuid != null) tag.putUUID("owner", ownerUuid);
        tag.putString("name", companionName);
        tag.putString("dimension", dimensionId);
        tag.putLong("position", lastPosition.asLong());
        tag.putString("mode", mode.name());
        tag.putLong("latestRequest", latestRequestId);
        if (activeBlueprintId != null) tag.putUUID("blueprint", activeBlueprintId);
        tag.putString("task", activeTask);
        tag.putInt("agitation", agitation);
        tag.putLong("lastSummon", lastSummonGameTime);
        tag.putLong("lastAgitationUpdate", lastAgitationUpdate);

        ListTag episodeTags = new ListTag();
        episodes.forEach(memory -> episodeTags.add(memory.save()));
        tag.put("episodes", episodeTags);

        CompoundTag factTags = new CompoundTag();
        facts.forEach(factTags::putString);
        tag.put("facts", factTags);
        return tag;
    }

    private static CompanionSavedData load(CompoundTag tag) {
        CompanionSavedData data = new CompanionSavedData();
        if (tag.hasUUID("companion")) data.companionUuid = tag.getUUID("companion");
        if (tag.hasUUID("owner")) data.ownerUuid = tag.getUUID("owner");
        if (tag.contains("name", Tag.TAG_STRING)) data.companionName = limit(tag.getString("name"), 48);
        if (tag.contains("dimension", Tag.TAG_STRING)) data.dimensionId = tag.getString("dimension");
        if (tag.contains("position", Tag.TAG_LONG)) data.lastPosition = BlockPos.of(tag.getLong("position"));
        data.mode = CompanionMode.parse(tag.getString("mode"));
        data.latestRequestId = tag.getLong("latestRequest");
        if (tag.hasUUID("blueprint")) data.activeBlueprintId = tag.getUUID("blueprint");
        data.activeTask = limit(tag.getString("task"), 96);
        data.agitation = Math.max(0, Math.min(10, tag.getInt("agitation")));
        data.lastSummonGameTime = tag.contains("lastSummon", Tag.TAG_LONG)
                ? tag.getLong("lastSummon") : Long.MIN_VALUE;
        data.lastAgitationUpdate = tag.getLong("lastAgitationUpdate");

        ListTag episodes = tag.getList("episodes", Tag.TAG_COMPOUND);
        for (int i = Math.max(0, episodes.size() - MAX_EPISODES); i < episodes.size(); i++) {
            data.episodes.addLast(MemoryEntry.load(episodes.getCompound(i)));
        }

        CompoundTag facts = tag.getCompound("facts");
        for (String key : facts.getAllKeys()) {
            if (data.facts.size() >= MAX_FACTS) break;
            data.facts.put(limit(key, 64), limit(facts.getString(key), 160));
        }
        return data;
    }

    private void decayAgitation(long gameTime) {
        if (lastAgitationUpdate == 0) lastAgitationUpdate = gameTime;
        long elapsed = gameTime - lastAgitationUpdate;
        if (elapsed < 6000 || agitation == 0) return;
        int decay = (int) Math.min(agitation, elapsed / 6000);
        agitation -= decay;
        lastAgitationUpdate += decay * 6000L;
        setDirty();
    }

    private static String limit(String value, int maximum) {
        if (value == null) return "";
        return value.length() <= maximum ? value : value.substring(0, maximum);
    }
}

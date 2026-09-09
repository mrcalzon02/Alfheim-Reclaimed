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
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.SimpleContainer;
import com.continuityworks.alfheimcompanion.entity.ElvenCompanionEntity;
import net.minecraft.world.entity.EquipmentSlot;

public final class CompanionSavedData extends SavedData {
    private static final String DATA_NAME = "alfheim_companion_state";
    private static final int DATA_VERSION = 7;
    public static final List<String> OUTFITS = List.of("wayfinder", "warden", "gardener", "ashen_scout", "winter_envoy");
    private static final int MAX_EPISODES = 50;
    private static final int MAX_FACTS = 64;
    private static final int MAX_OBSERVED_CHUNKS = 512;
    private static final int MAX_DELEGATED_CLAIMS = 128;

    private UUID companionUuid;
    private UUID ownerUuid;
    private String companionName = "";
    private String dimensionId = "minecraft:overworld";
    private BlockPos lastPosition = BlockPos.ZERO;
    private CompanionMode mode = CompanionMode.DISMISSED;
    private long latestRequestId;
    private UUID activeBlueprintId;
    private ActiveTask activeTask = ActiveTask.NONE;
    private BlueprintLedger blueprintLedger = BlueprintLedger.NONE;
    private BaseObjective baseObjective = BaseObjective.NONE;
    private BehaviorPreset behaviorPreset = BehaviorPreset.BALANCED;
    private int agitation;
    private long lastSummonGameTime = Long.MIN_VALUE;
    private long lastAgitationUpdate;
    private long leaseExpiresGameTime;
    private int moodIndex;
    private long lastMoodUpdate;
    private int lastClaimPaperBalance;
    private AutonomousActivityPlan autonomousActivity = AutonomousActivityPlan.NONE;
    private final ArrayDeque<MemoryEntry> episodes = new ArrayDeque<>();
    private final LinkedHashMap<String, String> facts = new LinkedHashMap<>();
    private final LinkedHashMap<UUID, PlayerCompanionBinding> playerBindings = new LinkedHashMap<>();
    private final LinkedHashMap<UUID, FallenInventory> fallenInventories = new LinkedHashMap<>();
    private final LinkedHashMap<String, ObservedChunk> observedChunks = new LinkedHashMap<>();
    private final LinkedHashMap<String, DelegatedClaim> delegatedClaims = new LinkedHashMap<>();

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
    public String activeTask() { return activeTask.display(); }
    public ActiveTask task() { return activeTask; }
    public BlueprintLedger blueprintLedger() { return blueprintLedger; }
    public BaseObjective baseObjective() { return baseObjective; }
    public BehaviorPreset behaviorPreset() { return behaviorPreset; }
    public int agitation(long gameTime) {
        decayAgitation(gameTime);
        return agitation;
    }
    public List<MemoryEntry> episodes() { return List.copyOf(episodes); }
    public Map<String, String> facts() { return Collections.unmodifiableMap(facts); }
    public long leaseExpiresGameTime() { return leaseExpiresGameTime; }
    public int moodIndex() { return moodIndex; }
    public List<ObservedChunk> observedChunks() { return List.copyOf(observedChunks.values()); }
    public List<DelegatedClaim> delegatedClaims() { return List.copyOf(delegatedClaims.values()); }
    public int lastClaimPaperBalance() { return lastClaimPaperBalance; }
    public AutonomousActivityPlan autonomousActivity() { return autonomousActivity; }
    public Optional<PlayerCompanionBinding> playerBinding(UUID playerUuid) {
        return Optional.ofNullable(playerBindings.get(playerUuid));
    }

    public PlayerCompanionBinding getOrCreatePlayerBinding(UUID playerUuid, long randomSeed) {
        PlayerCompanionBinding existing = playerBindings.get(playerUuid);
        if (existing != null) return existing;
        UUID seed = new UUID(playerUuid.getMostSignificantBits() ^ randomSeed,
                playerUuid.getLeastSignificantBits() + randomSeed * 31L);
        PlayerCompanionBinding created = new PlayerCompanionBinding(ElvenNames.select(seed),
                OUTFITS.get(Math.floorMod(seed.hashCode(), OUTFITS.size())), true, 0);
        playerBindings.put(playerUuid, created);
        setDirty();
        return created;
    }

    public PlayerCompanionBinding resetPlayerBinding(UUID playerUuid, long randomSeed) {
        int deaths = playerBindings.containsKey(playerUuid) ? playerBindings.get(playerUuid).deaths() : 0;
        playerBindings.remove(playerUuid);
        PlayerCompanionBinding generated = getOrCreatePlayerBinding(playerUuid, randomSeed + deaths * 9973L + 1);
        PlayerCompanionBinding fresh = new PlayerCompanionBinding(generated.name(), generated.outfit(), true, deaths);
        playerBindings.put(playerUuid, fresh);
        if (playerUuid.equals(ownerUuid)) companionName = fresh.name();
        setDirty();
        return fresh;
    }

    public void activatePlayerBinding(UUID playerUuid, long randomSeed) {
        PlayerCompanionBinding binding = getOrCreatePlayerBinding(playerUuid, randomSeed);
        companionName = binding.name();
        setDirty();
    }

    public boolean setPlayerProfile(UUID playerUuid, String name, long randomSeed) {
        if (!ElvenNames.all().contains(name)) return false;
        PlayerCompanionBinding old = getOrCreatePlayerBinding(playerUuid, randomSeed);
        playerBindings.put(playerUuid, new PlayerCompanionBinding(name, old.outfit(), old.alive(), old.deaths()));
        if (playerUuid.equals(ownerUuid)) companionName = name;
        setDirty();
        return true;
    }

    public boolean setPlayerOutfit(UUID playerUuid, String outfit, long randomSeed) {
        if (!OUTFITS.contains(outfit)) return false;
        PlayerCompanionBinding old = getOrCreatePlayerBinding(playerUuid, randomSeed);
        playerBindings.put(playerUuid, new PlayerCompanionBinding(old.name(), outfit, old.alive(), old.deaths()));
        setDirty();
        return true;
    }

    public void markCurrentBindingDead() {
        if (ownerUuid == null) return;
        PlayerCompanionBinding old = playerBindings.get(ownerUuid);
        if (old == null) old = new PlayerCompanionBinding(companionName(), "wayfinder", true, 0);
        playerBindings.put(ownerUuid, new PlayerCompanionBinding(old.name(), old.outfit(), false, old.deaths() + 1));
        leaseExpiresGameTime = 0;
        setDirty();
    }

    public void storeFallenInventory(UUID playerUuid, List<ItemStack> contents,
                                     Map<String, ItemStack> equipment) {
        fallenInventories.put(playerUuid, new FallenInventory(contents.stream().filter(stack -> !stack.isEmpty())
                .limit(36).map(ItemStack::copy).toList(), equipment.entrySet().stream()
                .filter(entry -> !entry.getValue().isEmpty()).collect(java.util.stream.Collectors.toMap(
                        Map.Entry::getKey, entry -> entry.getValue().copy()))));
        setDirty();
    }

    public void restoreFallenInventory(UUID playerUuid, ElvenCompanionEntity companion) {
        FallenInventory saved = fallenInventories.remove(playerUuid);
        if (saved == null) return;
        saved.equipment.forEach((slotName, stack) -> {
            for (EquipmentSlot slot : EquipmentSlot.values()) {
                if (slot.getName().equals(slotName)) companion.setItemSlot(slot, stack.copy());
            }
        });
        for (ItemStack stack : saved.contents) {
            ItemStack remainder = companion.inventory().addItem(stack.copy());
            // This should only occur if a future inventory shrink makes the saved set too large.
            if (!remainder.isEmpty()) companion.spawnAtLocation(remainder);
        }
        setDirty();
    }

    public void adjustMood(int change, long gameTime) {
        decayMood(gameTime);
        moodIndex = Math.max(-100, Math.min(100, moodIndex + change));
        lastMoodUpdate = gameTime;
        setDirty();
    }

    public boolean leaseHeldByOther(UUID playerUuid, long gameTime) {
        return ownerUuid != null && !ownerUuid.equals(playerUuid) && leaseExpiresGameTime > gameTime;
    }

    public boolean leaseHeldBy(UUID playerUuid, long gameTime) {
        return ownerUuid != null && ownerUuid.equals(playerUuid) && leaseExpiresGameTime > gameTime;
    }

    public void claimOrRefreshLease(UUID playerUuid, long gameTime) {
        ownerUuid = playerUuid;
        leaseExpiresGameTime = Math.max(0, gameTime) + 36_000L;
        setDirty();
    }

    public boolean expireLease(long gameTime) {
        if (leaseExpiresGameTime == 0 || gameTime < leaseExpiresGameTime) return false;
        leaseExpiresGameTime = 0;
        activeTask = ActiveTask.NONE;
        if (autonomousActivity.active()) autonomousActivity = autonomousActivity.advance(
                AutonomousActivityPlan.State.PAUSED, autonomousActivity.progress(), gameTime,
                "lease expired");
        setDirty();
        return true;
    }

    public void releaseLease() {
        leaseExpiresGameTime = 0;
        setDirty();
    }

    /** Prevents a new lessee from receiving the previous player's task or quest context. */
    public void clearOwnerContext() {
        episodes.removeIf(memory -> memory.type().equals("request") || memory.type().equals("quest"));
        facts.keySet().removeIf(key -> key.startsWith("quest:") || key.equals("guard_anchor"));
        activeTask = ActiveTask.NONE;
        baseObjective = BaseObjective.NONE;
        autonomousActivity = AutonomousActivityPlan.NONE;
        setDirty();
    }

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
        this.activeTask = ActiveTask.migrate(task);
        this.activeBlueprintId = blueprintId;
        setDirty();
    }

    public void setTask(ActiveTask task, UUID blueprintId) {
        this.activeTask = task == null ? ActiveTask.NONE : task;
        this.activeBlueprintId = blueprintId;
        setDirty();
    }

    public void setBlueprintLedger(BlueprintLedger ledger) {
        this.blueprintLedger = ledger == null ? BlueprintLedger.NONE : ledger;
        this.activeBlueprintId = this.blueprintLedger.blueprintId();
        setDirty();
    }

    public void setBaseObjective(BaseObjective objective) {
        this.baseObjective = objective == null ? BaseObjective.NONE : objective;
        setDirty();
    }

    public void setBehaviorPreset(BehaviorPreset preset) {
        this.behaviorPreset = preset == null ? BehaviorPreset.BALANCED : preset;
        setDirty();
    }

    public void observeChunk(String dimensionId, int chunkX, int chunkZ, long gameTime) {
        ObservedChunk observed = new ObservedChunk(dimensionId, chunkX, chunkZ, gameTime);
        ObservedChunk previous = observedChunks.get(observed.key());
        if (previous != null && gameTime - previous.observedGameTime() < 1200L) return;
        observedChunks.remove(observed.key());
        observedChunks.put(observed.key(), observed);
        while (observedChunks.size() > MAX_OBSERVED_CHUNKS)
            observedChunks.remove(observedChunks.keySet().iterator().next());
        setDirty();
    }

    public boolean hasObservedChunk(String dimensionId, int chunkX, int chunkZ) {
        return observedChunks.containsKey(ObservedChunk.key(dimensionId, chunkX, chunkZ));
    }

    public void recordDelegatedClaim(DelegatedClaim claim) {
        if (claim == null) return;
        delegatedClaims.remove(claim.key());
        delegatedClaims.put(claim.key(), claim);
        while (delegatedClaims.size() > MAX_DELEGATED_CLAIMS)
            delegatedClaims.remove(delegatedClaims.keySet().iterator().next());
        setDirty();
    }

    public void removeDelegatedClaim(String dimensionId, int chunkX, int chunkZ) {
        if (delegatedClaims.remove(DelegatedClaim.key(dimensionId, chunkX, chunkZ)) != null) setDirty();
    }

    public void setLastClaimPaperBalance(int count) {
        int bounded = Math.max(0, Math.min(1728, count));
        if (lastClaimPaperBalance == bounded) return;
        lastClaimPaperBalance = bounded;
        setDirty();
    }

    public void setAutonomousActivity(AutonomousActivityPlan plan) {
        this.autonomousActivity = plan == null ? AutonomousActivityPlan.NONE : plan;
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
        activeTask = ActiveTask.NONE;
        activeBlueprintId = null;
        if (autonomousActivity.active()) autonomousActivity = autonomousActivity.advance(
                AutonomousActivityPlan.State.PAUSED, autonomousActivity.progress(),
                autonomousActivity.updatedGameTime(), "companion dismissed");
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
        tag.put("activeTask", activeTask.save());
        tag.put("blueprintLedger", blueprintLedger.save());
        tag.put("baseObjective", baseObjective.save());
        tag.putString("behaviorPreset", behaviorPreset.name());
        tag.putInt("agitation", agitation);
        tag.putLong("lastSummon", lastSummonGameTime);
        tag.putLong("lastAgitationUpdate", lastAgitationUpdate);
        tag.putLong("leaseExpires", leaseExpiresGameTime);
        tag.putInt("mood", moodIndex);
        tag.putLong("lastMoodUpdate", lastMoodUpdate);
        tag.putInt("lastClaimPaperBalance", lastClaimPaperBalance);
        tag.put("autonomousActivity", autonomousActivity.save());

        ListTag episodeTags = new ListTag();
        episodes.forEach(memory -> episodeTags.add(memory.save()));
        tag.put("episodes", episodeTags);

        CompoundTag factTags = new CompoundTag();
        facts.forEach(factTags::putString);
        tag.put("facts", factTags);
        ListTag bindingTags = new ListTag();
        playerBindings.forEach((player, binding) -> {
            CompoundTag entry = binding.save();
            entry.putUUID("player", player);
            bindingTags.add(entry);
        });
        tag.put("playerBindings", bindingTags);
        ListTag fallenTags = new ListTag();
        fallenInventories.forEach((player, saved) -> {
            CompoundTag entry = new CompoundTag();
            entry.putUUID("player", player);
            ListTag items = new ListTag();
            saved.contents.forEach(stack -> items.add(stack.save(new CompoundTag())));
            entry.put("items", items);
            CompoundTag equipment = new CompoundTag();
            saved.equipment.forEach((slot, stack) -> equipment.put(slot, stack.save(new CompoundTag())));
            entry.put("equipment", equipment);
            fallenTags.add(entry);
        });
        tag.put("fallenInventories", fallenTags);
        ListTag observedTags = new ListTag();
        observedChunks.values().forEach(observed -> observedTags.add(observed.save()));
        tag.put("observedChunks", observedTags);
        ListTag delegatedTags = new ListTag();
        delegatedClaims.values().forEach(claim -> delegatedTags.add(claim.save()));
        tag.put("delegatedClaims", delegatedTags);
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
        data.activeTask = tag.contains("activeTask", Tag.TAG_COMPOUND)
                ? ActiveTask.load(tag.getCompound("activeTask"))
                : ActiveTask.migrate(tag.getString("task"));
        data.blueprintLedger = tag.contains("blueprintLedger", Tag.TAG_COMPOUND)
                ? BlueprintLedger.load(tag.getCompound("blueprintLedger")) : BlueprintLedger.NONE;
        data.baseObjective = tag.contains("baseObjective", Tag.TAG_COMPOUND)
                ? BaseObjective.load(tag.getCompound("baseObjective")) : BaseObjective.NONE;
        data.behaviorPreset = BehaviorPreset.parse(tag.getString("behaviorPreset"))
                .orElse(BehaviorPreset.BALANCED);
        data.agitation = Math.max(0, Math.min(10, tag.getInt("agitation")));
        data.lastSummonGameTime = tag.contains("lastSummon", Tag.TAG_LONG)
                ? tag.getLong("lastSummon") : Long.MIN_VALUE;
        data.lastAgitationUpdate = tag.getLong("lastAgitationUpdate");
        data.leaseExpiresGameTime = Math.max(0, tag.getLong("leaseExpires"));
        data.moodIndex = Math.max(-100, Math.min(100, tag.getInt("mood")));
        data.lastMoodUpdate = Math.max(0, tag.getLong("lastMoodUpdate"));
        data.lastClaimPaperBalance = Math.max(0, Math.min(1728, tag.getInt("lastClaimPaperBalance")));
        data.autonomousActivity = tag.contains("autonomousActivity", Tag.TAG_COMPOUND)
                ? AutonomousActivityPlan.load(tag.getCompound("autonomousActivity"))
                : AutonomousActivityPlan.NONE;

        ListTag episodes = tag.getList("episodes", Tag.TAG_COMPOUND);
        for (int i = Math.max(0, episodes.size() - MAX_EPISODES); i < episodes.size(); i++) {
            data.episodes.addLast(MemoryEntry.load(episodes.getCompound(i)));
        }

        CompoundTag facts = tag.getCompound("facts");
        for (String key : facts.getAllKeys()) {
            if (data.facts.size() >= MAX_FACTS) break;
            data.facts.put(limit(key, 64), limit(facts.getString(key), 160));
        }
        ListTag bindings = tag.getList("playerBindings", Tag.TAG_COMPOUND);
        for (int i = 0; i < bindings.size() && data.playerBindings.size() < 256; i++) {
            CompoundTag entry = bindings.getCompound(i);
            if (entry.hasUUID("player")) data.playerBindings.put(entry.getUUID("player"), PlayerCompanionBinding.load(entry));
        }
        // Preserve the original singleton identity when migrating pre-binding saves.
        if (data.ownerUuid != null && !data.companionName.isBlank() && !data.playerBindings.containsKey(data.ownerUuid)) {
            data.playerBindings.put(data.ownerUuid,
                    new PlayerCompanionBinding(data.companionName, "wayfinder", true, 0));
        }
        ListTag fallen = tag.getList("fallenInventories", Tag.TAG_COMPOUND);
        for (int i = 0; i < fallen.size() && data.fallenInventories.size() < 256; i++) {
            CompoundTag entry = fallen.getCompound(i);
            if (!entry.hasUUID("player")) continue;
            ListTag items = entry.getList("items", Tag.TAG_COMPOUND);
            List<ItemStack> stacks = new java.util.ArrayList<>();
            for (int item = 0; item < items.size() && stacks.size() < 42; item++)
                stacks.add(ItemStack.of(items.getCompound(item)));
            CompoundTag equipmentTag = entry.getCompound("equipment");
            Map<String, ItemStack> equipment = new LinkedHashMap<>();
            for (String slot : equipmentTag.getAllKeys()) equipment.put(slot, ItemStack.of(equipmentTag.getCompound(slot)));
            data.fallenInventories.put(entry.getUUID("player"), new FallenInventory(stacks, equipment));
        }
        ListTag observed = tag.getList("observedChunks", Tag.TAG_COMPOUND);
        for (int i = Math.max(0, observed.size() - MAX_OBSERVED_CHUNKS); i < observed.size(); i++) {
            ObservedChunk chunk = ObservedChunk.load(observed.getCompound(i));
            if (chunk != null) data.observedChunks.put(chunk.key(), chunk);
        }
        ListTag delegated = tag.getList("delegatedClaims", Tag.TAG_COMPOUND);
        for (int i = Math.max(0, delegated.size() - MAX_DELEGATED_CLAIMS); i < delegated.size(); i++) {
            DelegatedClaim claim = DelegatedClaim.load(delegated.getCompound(i));
            if (claim != null) data.delegatedClaims.put(claim.key(), claim);
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

    private void decayMood(long gameTime) {
        if (lastMoodUpdate == 0) lastMoodUpdate = gameTime;
        long elapsed = Math.max(0, gameTime - lastMoodUpdate);
        int steps = (int) Math.min(100, elapsed / 12_000L);
        if (steps == 0 || moodIndex == 0) return;
        moodIndex += moodIndex > 0 ? -Math.min(moodIndex, steps) : Math.min(-moodIndex, steps);
        lastMoodUpdate += steps * 12_000L;
    }

    private static String limit(String value, int maximum) {
        if (value == null) return "";
        return value.length() <= maximum ? value : value.substring(0, maximum);
    }

    private record FallenInventory(List<ItemStack> contents, Map<String, ItemStack> equipment) {}
}

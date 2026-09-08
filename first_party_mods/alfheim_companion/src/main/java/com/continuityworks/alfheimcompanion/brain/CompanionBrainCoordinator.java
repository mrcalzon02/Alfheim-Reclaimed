package com.continuityworks.alfheimcompanion.brain;

import com.continuityworks.alfheimcompanion.AlfheimCompanion;
import com.continuityworks.alfheimcompanion.entity.ElvenCompanionEntity;
import com.continuityworks.alfheimcompanion.memory.CompanionMode;
import com.continuityworks.alfheimcompanion.memory.CompanionSavedData;
import com.continuityworks.alfheimcompanion.service.CompanionSummonService;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.phys.AABB;

import java.util.Comparator;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.CompletionException;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.Optional;
import com.continuityworks.alfheimcompanion.integration.QuestAwarenessBridge;

public final class CompanionBrainCoordinator {
    private static final int MAX_RESULT_AGE_TICKS = 100;
    private static final AtomicBoolean IN_FLIGHT = new AtomicBoolean();
    private static final ConcurrentLinkedQueue<CompletedPlan> RESULTS = new ConcurrentLinkedQueue<>();
    private static final ConcurrentLinkedQueue<CompletedAmbient> AMBIENT_RESULTS = new ConcurrentLinkedQueue<>();
    private static volatile TinyBrainEngine engine = new RuleBasedTinyBrainEngine();
    private static long lastAmbientGameTime;

    private CompanionBrainCoordinator() {}

    public static synchronized void installEngine(TinyBrainEngine replacement) {
        if (replacement == null) throw new IllegalArgumentException("replacement");
        TinyBrainEngine previous = engine;
        engine = replacement;
        previous.close();
        IN_FLIGHT.set(false);
        RESULTS.clear();
        AMBIENT_RESULTS.clear();
        AlfheimCompanion.LOGGER.info("Installed tiny-brain engine {}", replacement.engineId());
    }

    public static void tick(MinecraftServer server) {
        CompanionSavedData data = CompanionSavedData.get(server);
        applyCompleted(server, data);
        applyAmbient(server, data);
        if (server.getTickCount() % 200 == 0) maybeRequestAmbient(server, data);
    }

    /**
     * Explicit entry point for construction interpretation and other non-routine reasoning.
     * Combat, following, waiting and scripted interactions must not call this method.
     */
    public static boolean requestComplexPlan(MinecraftServer server) {
        if (IN_FLIGHT.get()) return false;
        CompanionSavedData data = CompanionSavedData.get(server);

        ElvenCompanionEntity companion = CompanionSummonService.findLoaded(server,
                data.companionUuid().orElse(null));
        if (companion == null || data.mode() == CompanionMode.DISMISSED) return false;
        ServerPlayer owner = companion.resolveOwner();
        if (owner == null || owner.level() != companion.level()) return false;

        long requestId = data.nextRequestId();
        BrainSnapshot snapshot = snapshot(requestId, companion, owner, data);
        if (!IN_FLIGHT.compareAndSet(false, true)) return false;

        engine.activate();
        engine.plan(snapshot).orTimeout(4, TimeUnit.SECONDS).whenComplete((result, error) -> {
            if (error == null && result != null) RESULTS.offer(new CompletedPlan(result, snapshot.gameTime()));
            else if (!(error instanceof CompletionException))
                AlfheimCompanion.LOGGER.debug("Tiny-brain plan dropped", error);
            IN_FLIGHT.set(false);
        });
        return true;
    }

    public static void deactivate() {
        RESULTS.clear();
        AMBIENT_RESULTS.clear();
        IN_FLIGHT.set(false);
        engine.deactivate();
    }

    public static void clear(UUID companionUuid) {
        RESULTS.clear();
        IN_FLIGHT.set(false);
    }

    private static BrainSnapshot snapshot(long requestId, ElvenCompanionEntity companion,
                                          ServerPlayer owner, CompanionSavedData data) {
        AABB area = companion.getBoundingBox().inflate(12.0D, 6.0D, 12.0D);
        List<BrainSnapshot.Threat> threats = companion.level()
                .getEntitiesOfClass(Monster.class, area, Entity::isAlive).stream()
                .sorted(Comparator.comparingDouble(companion::distanceToSqr))
                .limit(3)
                .map(entity -> new BrainSnapshot.Threat(entity.getId(),
                        entity.getType().toString(), (int) companion.distanceToSqr(entity)))
                .toList();
        int hp = owner.getMaxHealth() <= 0 ? 0
                : Math.round(owner.getHealth() * 100.0F / owner.getMaxHealth());
        return new BrainSnapshot(requestId, companion.level().getGameTime(), companion.getUUID(),
                owner.getUUID(), companion.level().dimension().location().toString(),
                companion.blockPosition(), owner.blockPosition(), hp, threats,
                data.activeTask(), data.facts());
    }

    private static void applyCompleted(MinecraftServer server, CompanionSavedData data) {
        CompletedPlan completed;
        while ((completed = RESULTS.poll()) != null) {
            BrainDecision result = completed.decision();
            if (result.requestId() != data.latestRequestId()) continue;
            ElvenCompanionEntity companion = CompanionSummonService.findLoaded(server,
                    data.companionUuid().orElse(null));
            if (companion == null || !companion.isAlive()) continue;
            if (companion.level().getGameTime() - completed.issuedGameTime() > MAX_RESULT_AGE_TICKS) continue;

            CompanionMode mode = switch (result.directive()) {
                case DEFEND -> CompanionMode.DEFENDING;
                case RETREAT -> CompanionMode.RETREATING;
                case WAIT -> CompanionMode.WAITING;
                case REQUEST_BLUEPRINT, EXECUTE_TASK -> CompanionMode.WORKING;
                default -> CompanionMode.FOLLOWING;
            };
            companion.setMode(mode);
            ServerPlayer owner = companion.resolveOwner();
            if (owner != null && !result.dialogue().isBlank()) {
                owner.sendSystemMessage(Component.literal("§d[" + data.companionName() + "] §f"
                        + result.dialogue()));
            }
        }
    }

    private static void maybeRequestAmbient(MinecraftServer server, CompanionSavedData data) {
        if (IN_FLIGHT.get() || !data.activeTask().isBlank()) return;
        ElvenCompanionEntity companion = CompanionSummonService.findLoaded(server,
                data.companionUuid().orElse(null));
        if (companion == null || (companion.mode() != CompanionMode.FOLLOWING
                && companion.mode() != CompanionMode.WAITING)) return;
        ServerPlayer owner = companion.resolveOwner();
        if (owner == null || owner.level() != companion.level() || companion.distanceToSqr(owner) > 1024.0D) return;
        long now = companion.level().getGameTime();
        if (now - lastAmbientGameTime < 12000) return;
        AABB calmArea = companion.getBoundingBox().inflate(16.0D, 8.0D, 16.0D);
        if (!companion.level().getEntitiesOfClass(Monster.class, calmArea, Entity::isAlive).isEmpty()) return;

        String biome = companion.level().getBiome(companion.blockPosition()).unwrapKey()
                .map(key -> key.location().toString()).orElse("unknown");
        String time = companion.level().isNight() ? "night"
                : (companion.level().getDayTime() % 24000L < 2000L ? "dawn" : "day");
        String weather = companion.level().isThundering() ? "thunder"
                : (companion.level().isRaining() ? "rain" : "clear");
        String quest = QuestAwarenessBridge.provider().flatMap(provider -> provider.questsFor(owner).stream()
                .filter(q -> q.status() == com.continuityworks.alfheimcompanion.api.quest.QuestProvider.Status.ACTIVE)
                .findFirst().map(q -> q.name() + ": " + q.goal())).orElse("");
        List<String> memories = data.episodes().stream()
                .sorted(Comparator.comparingInt(com.continuityworks.alfheimcompanion.memory.MemoryEntry::importance).reversed())
                .limit(3).map(memory -> memory.subject() + ": " + memory.detail()).toList();
        long requestId = data.nextRequestId();
        AmbientSnapshot snapshot = new AmbientSnapshot(requestId, now, companion.getUUID(), owner.getUUID(),
                companion.level().dimension().location().toString(), biome, time, weather,
                companion.mode().name().toLowerCase(), quest, memories);
        if (!IN_FLIGHT.compareAndSet(false, true)) return;
        lastAmbientGameTime = now;
        engine.activate();
        engine.reflect(snapshot).orTimeout(4, TimeUnit.SECONDS).whenComplete((line, error) -> {
            if (error == null && line != null && line.isPresent() && !line.get().isBlank()) {
                AMBIENT_RESULTS.offer(new CompletedAmbient(requestId, now,
                        line.get().substring(0, Math.min(120, line.get().length()))));
            }
            IN_FLIGHT.set(false);
        });
    }

    private static void applyAmbient(MinecraftServer server, CompanionSavedData data) {
        CompletedAmbient completed;
        while ((completed = AMBIENT_RESULTS.poll()) != null) {
            if (completed.requestId() != data.latestRequestId()) continue;
            ElvenCompanionEntity companion = CompanionSummonService.findLoaded(server,
                    data.companionUuid().orElse(null));
            if (companion == null || companion.level().getGameTime() - completed.issuedGameTime() > MAX_RESULT_AGE_TICKS) continue;
            ServerPlayer owner = companion.resolveOwner();
            if (owner != null) owner.sendSystemMessage(Component.literal("§d[" + data.companionName()
                    + "] §f" + completed.line()));
        }
    }

    private record CompletedPlan(BrainDecision decision, long issuedGameTime) {}
    private record CompletedAmbient(long requestId, long issuedGameTime, String line) {}
}

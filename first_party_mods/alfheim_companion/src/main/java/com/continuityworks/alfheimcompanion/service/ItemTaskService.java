package com.continuityworks.alfheimcompanion.service;

import com.continuityworks.alfheimcompanion.entity.ElvenCompanionEntity;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.Item;
import net.minecraft.world.phys.AABB;

import java.util.Comparator;
import java.util.Optional;

public final class ItemTaskService {
    public enum Approach { SHOW, FETCH, LEAD }
    public record StartResult(boolean started, String message) {}

    private ItemTaskService() {}

    public static StartResult start(ServerPlayer owner, ElvenCompanionEntity companion,
                                    String query, int count, Approach approach) {
        Optional<Item> item = ItemResolver.resolve(query);
        if (item.isEmpty()) return new StartResult(false, "I do not recognize an item called " + query + ".");
        AABB area = companion.getBoundingBox().inflate(32.0D, 16.0D, 32.0D);
        Optional<ItemEntity> nearest = companion.level().getEntitiesOfClass(ItemEntity.class, area,
                        entity -> entity.isAlive() && entity.getItem().is(item.get())).stream()
                .min(Comparator.comparingDouble(companion::distanceToSqr));
        if (nearest.isEmpty()) {
            return new StartResult(false, "I cannot see a dropped " + item.get().getDescription().getString()
                    + " within thirty-two blocks. I will need a remembered location or permitted container search.");
        }
        ItemEntity found = nearest.get();
        if (approach == Approach.SHOW) {
            return new StartResult(true, "I see it near " + found.blockPosition().toShortString() + ".");
        }
        companion.beginItemTask(found.getUUID(), Math.max(1, count), approach == Approach.FETCH);
        return new StartResult(true, approach == Approach.FETCH
                ? "I see it. I will retrieve it and return."
                : "I see it. Follow me and I will take you there.");
    }
}

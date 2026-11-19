"""Compile the ACTUAL companion death/dismiss service against tiny Java stand-ins.

This isolates the production method's item-copy, ownership and clear ordering from Forge,
and runs with Java 17. It does NOT establish a successful Minecraft or Forge runtime build.
"""
from pathlib import Path
import shutil
import subprocess
import tempfile

PRODUCTION = Path(
    "first_party_mods/alfheim_companion/src/main/java/"
    "com/continuityworks/alfheimcompanion/service/CompanionDeathInventoryService.java"
)

STUBS = {
    "net/minecraft/world/item/ItemStack.java": r'''
package net.minecraft.world.item;
public final class ItemStack {
    public static final ItemStack EMPTY = new ItemStack("", 0);
    public final String id;
    public final int count;
    public ItemStack(String id, int count) { this.id = id; this.count = count; }
    public boolean isEmpty() { return count <= 0; }
    public ItemStack copy() { return new ItemStack(id, count); }
}
''',
    "net/minecraft/world/entity/EquipmentSlot.java": r'''
package net.minecraft.world.entity;
public enum EquipmentSlot {
    HEAD, CHEST, LEGS, FEET, MAINHAND, OFFHAND;
    public String getName() { return name().toLowerCase(java.util.Locale.ROOT); }
}
''',
    "net/minecraft/world/level/GameRules.java": r'''
package net.minecraft.world.level;
public class GameRules {
    public static final String RULE_KEEPINVENTORY = "keepInventory";
    public boolean keep = false;
    public boolean getBoolean(String key) { return keep; }
}
''',
    "net/minecraft/server/level/ServerPlayer.java": r'''
package net.minecraft.server.level;
public class ServerPlayer {}
''',
    "com/continuityworks/alfheimcompanion/integration/GraveIntegrationBridge.java": r'''
package com.continuityworks.alfheimcompanion.integration;
import com.continuityworks.alfheimcompanion.entity.ElvenCompanionEntity;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import java.util.List;
public class GraveIntegrationBridge {
    public static boolean capture(ServerPlayer player, ElvenCompanionEntity entity, List<ItemStack> items) {
        return false;
    }
}
''',
    "com/continuityworks/alfheimcompanion/memory/CompanionSavedData.java": r'''
package com.continuityworks.alfheimcompanion.memory;
import java.util.*;
import net.minecraft.world.item.ItemStack;
public class CompanionSavedData {
    public record Snapshot(List<ItemStack> carried, Map<String, ItemStack> equipment) {}
    public final Map<UUID, Snapshot> saved = new HashMap<>();
    public boolean failStore;
    public void storeFallenInventory(UUID owner, List<ItemStack> carried, Map<String, ItemStack> equipment) {
        if (failStore) throw new IllegalStateException("simulated save failure");
        List<ItemStack> cargoCopy = carried.stream().map(ItemStack::copy).toList();
        Map<String, ItemStack> equipmentCopy = new HashMap<>();
        equipment.forEach((key, stack) -> equipmentCopy.put(key, stack.copy()));
        saved.put(owner, new Snapshot(cargoCopy, equipmentCopy));
    }
}
''',
    "com/continuityworks/alfheimcompanion/entity/ElvenCompanionEntity.java": r'''
package com.continuityworks.alfheimcompanion.entity;
import java.util.*;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.level.GameRules;
import net.minecraft.server.level.ServerPlayer;
public class ElvenCompanionEntity {
    private final UUID owner;
    private final Cargo cargo = new Cargo();
    private final EnumMap<EquipmentSlot, ItemStack> equipped = new EnumMap<>(EquipmentSlot.class);
    private final StubLevel level = new StubLevel();
    public final List<ItemStack> drops = new ArrayList<>();
    public ElvenCompanionEntity(UUID owner) { this.owner = owner; }
    public UUID ownerUuid() { return owner; }
    public Cargo inventory() { return cargo; }
    public ItemStack getItemBySlot(EquipmentSlot slot) { return equipped.getOrDefault(slot, ItemStack.EMPTY); }
    public void setItemSlot(EquipmentSlot slot, ItemStack stack) { equipped.put(slot, stack); }
    public ServerPlayer resolveOwner() { return new ServerPlayer(); }
    public StubLevel level() { return level; }
    public void spawnAtLocation(ItemStack stack) { drops.add(stack.copy()); }
    public static final class StubLevel {
        private final GameRules rules = new GameRules();
        public GameRules getGameRules() { return rules; }
    }
    public static final class Cargo {
        private final ItemStack[] slots = new ItemStack[36];
        public Cargo() { Arrays.fill(slots, ItemStack.EMPTY); }
        public int getContainerSize() { return slots.length; }
        public ItemStack getItem(int slot) { return slots[slot]; }
        public void setItem(int slot, ItemStack item) { slots[slot] = item; }
        public void clearContent() { Arrays.fill(slots, ItemStack.EMPTY); }
    }
}
''',
    "com/continuityworks/alfheimcompanion/service/CompanionDismissRetentionTest.java": r'''
package com.continuityworks.alfheimcompanion.service;
import java.util.UUID;
import com.continuityworks.alfheimcompanion.entity.ElvenCompanionEntity;
import com.continuityworks.alfheimcompanion.memory.CompanionSavedData;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.ItemStack;
public final class CompanionDismissRetentionTest {
    static void require(boolean value, String message) {
        if (!value) throw new AssertionError(message);
    }
    public static void main(String[] args) {
        UUID alice = UUID.randomUUID();
        UUID bob = UUID.randomUUID();

        ElvenCompanionEntity entity = new ElvenCompanionEntity(alice);
        ItemStack cargo = new ItemStack("dreamwood", 12);
        ItemStack helmet = new ItemStack("elven_helm", 1);
        entity.inventory().setItem(0, cargo);
        entity.inventory().setItem(17, new ItemStack("rune", 4));
        entity.setItemSlot(EquipmentSlot.HEAD, helmet);
        entity.setItemSlot(EquipmentSlot.MAINHAND, new ItemStack("blade", 1));
        CompanionSavedData data = new CompanionSavedData();

        require(!CompanionDeathInventoryService.retainForDismiss(entity, data, bob),
                "other player's dismissal must fail closed");
        require(data.saved.isEmpty(), "cross-owner items were persisted");
        require(entity.inventory().getItem(0) == cargo, "cross-owner cargo changed");
        require(entity.getItemBySlot(EquipmentSlot.HEAD) == helmet, "cross-owner gear changed");

        require(CompanionDeathInventoryService.retainForDismiss(entity, data, alice),
                "legitimate owner cannot retain inventory");
        var saved = data.saved.get(alice);
        require(saved != null && saved.carried().size() == 2, "two cargo stacks not persisted");
        require(saved.carried().get(0) != cargo, "cargo must be copied");
        require(saved.carried().get(0).count == 12, "cargo quantity changed");
        require(saved.equipment().size() == 2, "equipment lost");
        require(saved.equipment().get("head") != helmet, "equipment not copied");
        require(saved.equipment().get("mainhand").id.equals("blade"), "mainhand lost");
        require(entity.inventory().getItem(0).isEmpty(), "retained cargo not cleared");
        require(entity.getItemBySlot(EquipmentSlot.HEAD).isEmpty(), "retained gear not cleared");
        require(entity.drops.isEmpty(), "dismissal incorrectly dropped gear in world");

        ElvenCompanionEntity failing = new ElvenCompanionEntity(alice);
        failing.inventory().setItem(0, new ItemStack("crystal", 9));
        failing.setItemSlot(EquipmentSlot.OFFHAND, new ItemStack("shield", 1));
        CompanionSavedData bad = new CompanionSavedData();
        bad.failStore = true;
        boolean threw = false;
        try { CompanionDeathInventoryService.retainForDismiss(failing, bad, alice); }
        catch (IllegalStateException expected) { threw = true; }
        require(threw, "failed storage must not masquerade as success");
        require(failing.inventory().getItem(0).count == 9, "failed save removed cargo");
        require(!failing.getItemBySlot(EquipmentSlot.OFFHAND).isEmpty(),
                "failed save removed equipment");

        ElvenCompanionEntity dead = new ElvenCompanionEntity(alice);
        dead.inventory().setItem(0, new ItemStack("berry", 6));
        dead.setItemSlot(EquipmentSlot.CHEST, new ItemStack("robe", 1));
        dead.level().getGameRules().keep = true;
        CompanionSavedData deathStore = new CompanionSavedData();
        CompanionDeathInventoryService.handle(dead, deathStore);
        require(deathStore.saved.containsKey(alice), "keepInventory death stopped preserving gear");
        require(deathStore.saved.get(alice).equipment().containsKey("chest"),
                "keepInventory lost equipped chest slot");
        require(dead.drops.isEmpty(), "keepInventory dropped items");

        ElvenCompanionEntity dropCase = new ElvenCompanionEntity(alice);
        dropCase.inventory().setItem(0, new ItemStack("berry", 6));
        dropCase.setItemSlot(EquipmentSlot.CHEST, new ItemStack("robe", 1));
        CompanionSavedData dropStore = new CompanionSavedData();
        CompanionDeathInventoryService.handle(dropCase, dropStore);
        require(dropCase.drops.size() == 2, "normal death should still drop both stacks");
        require(dropStore.saved.isEmpty(), "normal death changed save semantics");

        System.out.println("COMPANION_DISMISS_RETENTION_PASS: owner check, cargo/equipment copies, persistence-failure safety and unchanged death behavior");
    }
}
'''
}


def main():
    if not PRODUCTION.is_file():
        raise SystemExit(f"missing production source: {PRODUCTION}")
    with tempfile.TemporaryDirectory(prefix="alfheim-dismiss-java-") as tmp:
        root = Path(tmp)
        sources = root / "src"
        for name, body in STUBS.items():
            dest = sources / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(body.strip() + "\n", encoding="utf-8")
        dest = sources / "com/continuityworks/alfheimcompanion/service/CompanionDeathInventoryService.java"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(PRODUCTION, dest)
        classes = root / "classes"
        classes.mkdir()
        src = [str(file) for file in sources.rglob("*.java")]
        subprocess.run(["javac", "--release", "17", "-d", str(classes), *sorted(src)],
                       check=True)
        subprocess.run(["java", "-cp", str(classes),
                        "com.continuityworks.alfheimcompanion.service.CompanionDismissRetentionTest"],
                       check=True)


if __name__ == "__main__":
    main()

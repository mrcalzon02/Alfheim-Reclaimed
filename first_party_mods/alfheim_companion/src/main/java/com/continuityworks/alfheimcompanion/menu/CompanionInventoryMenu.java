package com.continuityworks.alfheimcompanion.menu;

import com.continuityworks.alfheimcompanion.entity.ElvenCompanionEntity;
import com.continuityworks.alfheimcompanion.registry.ModMenus;
import com.continuityworks.alfheimcompanion.integration.CombatProfileBridge;
import com.continuityworks.alfheimcompanion.service.EquipmentPolicy;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.world.Container;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.ItemStack;

public final class CompanionInventoryMenu extends AbstractContainerMenu {
    public static final int COMPANION_SLOTS = 36;
    public static final int EQUIPMENT_SLOTS = 6;
    public static final int COMPANION_MENU_SLOTS = COMPANION_SLOTS + EQUIPMENT_SLOTS;
    private static final EquipmentSlot[] EQUIPMENT_ORDER = {
            EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS,
            EquipmentSlot.FEET, EquipmentSlot.MAINHAND, EquipmentSlot.OFFHAND
    };
    private final ElvenCompanionEntity companion;
    private final Container container;

    public CompanionInventoryMenu(int containerId, Inventory playerInventory, ElvenCompanionEntity companion) {
        super(ModMenus.COMPANION_INVENTORY.get(), containerId);
        this.companion = companion;
        this.container = companion == null ? new SimpleContainer(COMPANION_SLOTS) : companion.inventory();
        checkContainerSize(container, COMPANION_SLOTS);
        container.startOpen(playerInventory.player);

        for (int index = 0; index < EQUIPMENT_ORDER.length; index++) {
            addSlot(new CompanionEquipmentSlot(index, EQUIPMENT_ORDER[index], 8 + index * 18, 18));
        }
        for (int row = 0; row < 4; row++) {
            for (int column = 0; column < 9; column++) {
                addSlot(new Slot(container, column + row * 9, 8 + column * 18, 36 + row * 18));
            }
        }
        for (int row = 0; row < 3; row++) {
            for (int column = 0; column < 9; column++) {
                addSlot(new Slot(playerInventory, column + row * 9 + 9, 8 + column * 18, 121 + row * 18));
            }
        }
        for (int column = 0; column < 9; column++) {
            addSlot(new Slot(playerInventory, column, 8 + column * 18, 179));
        }
    }

    public static CompanionInventoryMenu fromNetwork(int containerId, Inventory inventory, FriendlyByteBuf buffer) {
        var entity = inventory.player.level().getEntity(buffer.readVarInt());
        return new CompanionInventoryMenu(containerId, inventory,
                entity instanceof ElvenCompanionEntity companion ? companion : null);
    }

    @Override
    public boolean stillValid(Player player) {
        return companion != null && companion.isAlive() && player.getUUID().equals(companion.ownerUuid())
                && player.distanceToSqr(companion) <= 64.0D;
    }

    @Override
    public ItemStack quickMoveStack(Player player, int index) {
        Slot slot = slots.get(index);
        if (!slot.hasItem()) return ItemStack.EMPTY;
        ItemStack present = slot.getItem();
        ItemStack copy = present.copy();
        if (index < COMPANION_MENU_SLOTS) {
            if (!moveItemStackTo(present, COMPANION_MENU_SLOTS, slots.size(), true)) return ItemStack.EMPTY;
        } else {
            EquipmentPolicy.Decision decision = companion == null
                    ? new EquipmentPolicy.Decision(java.util.Optional.empty(), false, false, false)
                    : EquipmentPolicy.evaluate(companion, present);
            boolean moved = false;
            if (decision.slot().isPresent() && decision.eligible()) {
                int equipmentIndex = equipmentIndex(decision.slot().get());
                if (equipmentIndex >= 0) moved = moveItemStackTo(present, equipmentIndex, equipmentIndex + 1, false);
            }
            if (!moved && !moveItemStackTo(present, EQUIPMENT_SLOTS, COMPANION_MENU_SLOTS, false)) {
                return ItemStack.EMPTY;
            }
        }
        if (present.isEmpty()) slot.set(ItemStack.EMPTY); else slot.setChanged();
        return copy;
    }

    @Override
    public void removed(Player player) {
        super.removed(player);
        container.stopOpen(player);
    }

    private static int equipmentIndex(EquipmentSlot slot) {
        for (int i = 0; i < EQUIPMENT_ORDER.length; i++) if (EQUIPMENT_ORDER[i] == slot) return i;
        return -1;
    }

    private final class CompanionEquipmentSlot extends Slot {
        private final EquipmentSlot equipmentSlot;

        private CompanionEquipmentSlot(int index, EquipmentSlot equipmentSlot, int x, int y) {
            super(new SimpleContainer(EQUIPMENT_SLOTS), index, x, y);
            this.equipmentSlot = equipmentSlot;
        }

        @Override public ItemStack getItem() {
            return companion == null ? ItemStack.EMPTY : companion.getItemBySlot(equipmentSlot);
        }

        @Override public boolean hasItem() { return !getItem().isEmpty(); }

        @Override public void set(ItemStack stack) {
            if (companion != null) {
                companion.setItemSlot(equipmentSlot, stack);
                CombatProfileBridge.onEquipmentChanged(companion);
            }
            setChanged();
        }

        @Override public ItemStack remove(int amount) {
            ItemStack current = getItem();
            if (current.isEmpty()) return ItemStack.EMPTY;
            ItemStack removed = current.split(amount);
            if (current.isEmpty()) set(ItemStack.EMPTY); else setChanged();
            return removed;
        }

        @Override public boolean mayPlace(ItemStack stack) {
            if (companion == null) return false;
            EquipmentPolicy.Decision decision = EquipmentPolicy.evaluate(companion, stack);
            return decision.eligible() && decision.slot().filter(slot -> slot == equipmentSlot).isPresent();
        }

        @Override public int getMaxStackSize() { return 1; }

        @Override public void setChanged() {
            if (companion != null) CombatProfileBridge.onEquipmentChanged(companion);
        }
    }
}

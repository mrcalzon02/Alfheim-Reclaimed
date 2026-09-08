package com.continuityworks.alfheimcompanion.integration.mmo;

import com.continuityworks.alfheimcompanion.api.combat.CombatProfileProvider;
import com.robertx22.mine_and_slash.capability.entity.EntityData;
import com.robertx22.mine_and_slash.capability.player.PlayerData;
import com.robertx22.mine_and_slash.itemstack.ExileStack;
import com.robertx22.mine_and_slash.saveclasses.item_classes.GearItemData;
import com.robertx22.mine_and_slash.saveclasses.unit.ResourceType;
import com.robertx22.mine_and_slash.uncommon.interfaces.data_items.ICommonDataItem;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Optional;

/** Direct, version-pinned adapter for Mine and Slash 1.20.1-6.4.x public APIs. */
public final class MineAndSlashCombatProfileProvider implements CombatProfileProvider {
    @Override public int apiVersion() { return API_VERSION; }

    @Override
    public CombatProfile profile(ServerPlayer lessee, LivingEntity companion) {
        EntityData data = EntityData.get(companion);
        Map<String, Integer> resources = new LinkedHashMap<>();
        for (ResourceType type : ResourceType.getUsed()) {
            resources.put(type.GUID(), Math.round(data.getResources().get(companion, type)));
        }
        Map<String, Double> modifiers = new LinkedHashMap<>();
        data.getUnit().getStats().stats.forEach((id, stat) -> {
            if (stat != null && stat.isNotZero()) modifiers.put(id, (double) stat.getValue());
        });
        var classes = PlayerData.get(lessee).ascClass.allocatedSchoolsInOrder();
        String archetype = classes.isEmpty() ? "unassigned" : String.join("/", classes);
        return new CombatProfile("Mine and Slash", data.getLevel(), archetype, resources, modifiers);
    }

    @Override
    public boolean recognizes(ItemStack stack) {
        return gear(stack).isPresent();
    }

    @Override
    public Optional<EquipmentSlot> equipmentSlot(ItemStack stack) {
        return gear(stack).map(GearItemData::GetBaseGearType)
                .map(type -> type.getVanillaSlotType());
    }

    @Override
    public boolean mayEquip(LivingEntity companion, ItemStack stack) {
        Optional<GearItemData> gear = gear(stack);
        if (gear.isEmpty()) return true;
        EntityData data = EntityData.get(companion);
        GearItemData item = gear.get();
        return item.isValidItem() && item.canPlayerWear(data) && (!item.isWeapon() || data.canUseWeapon(item));
    }

    @Override
    public void synchronize(ServerPlayer lessee, LivingEntity companion) {
        EntityData ownerData = EntityData.get(lessee);
        EntityData companionData = EntityData.get(companion);
        int level = Math.max(1, ownerData.getLevel());
        if (companionData.getLevel() != level) {
            companionData.setLevel(level);
            companionData.setEquipsChanged();
        }
    }

    @Override
    public void onEquipmentChanged(LivingEntity companion) {
        EntityData.get(companion).setEquipsChanged();
    }

    private static Optional<GearItemData> gear(ItemStack stack) {
        if (stack.isEmpty()) return Optional.empty();
        try {
            ICommonDataItem<?> data = ICommonDataItem.load(stack);
            return data instanceof GearItemData gear ? Optional.of(gear) : Optional.empty();
        } catch (RuntimeException ignored) {
            return Optional.empty();
        }
    }
}

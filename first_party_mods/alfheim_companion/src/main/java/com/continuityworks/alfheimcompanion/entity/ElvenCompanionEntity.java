package com.continuityworks.alfheimcompanion.entity;

import com.continuityworks.alfheimcompanion.memory.CompanionMode;
import com.continuityworks.alfheimcompanion.memory.CompanionSavedData;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraft.world.level.Level;
import net.minecraftforge.network.NetworkHooks;
import com.continuityworks.alfheimcompanion.service.CompanionChunkTickets;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;

import java.util.UUID;

public final class ElvenCompanionEntity extends PathfinderMob {
    private UUID ownerUuid;
    private CompanionMode mode = CompanionMode.FOLLOWING;
    private final SimpleContainer inventory = new SimpleContainer(18);
    private UUID pendingOfferPlayer;
    private ItemStack pendingOffer = ItemStack.EMPTY;
    private long pendingOfferExpires;
    private BlockPos guardPosition;
    private UUID itemTaskTarget;
    private int itemTaskCount;
    private boolean itemTaskFetch;
    private boolean deliveryPending;
    private String deliveryItemId = "";
    private int deliveryCount;

    public ElvenCompanionEntity(EntityType<? extends PathfinderMob> type, Level level) {
        super(type, level);
        setPersistenceRequired();
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Mob.createMobAttributes()
                .add(Attributes.MAX_HEALTH, 40.0D)
                .add(Attributes.MOVEMENT_SPEED, 0.30D)
                .add(Attributes.ATTACK_DAMAGE, 4.0D)
                .add(Attributes.FOLLOW_RANGE, 32.0D);
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(0, new FloatGoal(this));
        goalSelector.addGoal(3, new FollowOwnerGoal(this));
        goalSelector.addGoal(2, new ItemTaskGoal(this));
        goalSelector.addGoal(4, new GuardPositionGoal(this));
        goalSelector.addGoal(7, new LookAtPlayerGoal(this, Player.class, 8.0F));
        goalSelector.addGoal(8, new RandomLookAroundGoal(this));
    }

    public void bindOwner(UUID ownerUuid) {
        this.ownerUuid = ownerUuid;
    }

    public UUID ownerUuid() {
        return ownerUuid;
    }

    public CompanionMode mode() {
        return mode;
    }

    public SimpleContainer inventory() {
        return inventory;
    }

    public void setMode(CompanionMode mode) {
        this.mode = mode;
        if (getServer() != null) CompanionSavedData.get(getServer()).setMode(mode);
    }

    public BlockPos guardPosition() { return guardPosition; }

    public void setGuardPosition(BlockPos position) { guardPosition = position == null ? null : position.immutable(); }

    public UUID itemTaskTarget() { return itemTaskTarget; }
    public int itemTaskCount() { return itemTaskCount; }
    public boolean itemTaskFetch() { return itemTaskFetch; }

    public void beginItemTask(UUID target, int count, boolean fetch) {
        itemTaskTarget = target;
        itemTaskCount = Math.max(1, Math.min(64, count));
        itemTaskFetch = fetch;
        setMode(CompanionMode.WORKING);
    }

    public void clearItemTask() {
        itemTaskTarget = null;
        itemTaskCount = 0;
        itemTaskFetch = false;
    }

    public void markDeliveryPending(ItemStack delivered, int count) {
        deliveryPending = true;
        deliveryItemId = String.valueOf(ForgeRegistries.ITEMS.getKey(delivered.getItem()));
        deliveryCount = Math.max(1, count);
    }

    public ServerPlayer resolveOwner() {
        return ownerUuid == null || getServer() == null
                ? null : getServer().getPlayerList().getPlayer(ownerUuid);
    }

    public void teleportNear(ServerPlayer owner) {
        if (owner.level() != level()) {
            changeDimension((ServerLevel) owner.level());
        }
        teleportTo(owner.getX() + 1.0D, owner.getY(), owner.getZ() + 1.0D);
    }

    @Override
    public void aiStep() {
        super.aiStep();
        if (!level().isClientSide && tickCount % 100 == 0 && getServer() != null) {
            CompanionSavedData.get(getServer()).updateLocation(
                    level().dimension().location().toString(), blockPosition());
        }
        if (!level().isClientSide && tickCount % 20 == 0) CompanionChunkTickets.update(this);
        if (!level().isClientSide && deliveryPending && tickCount % 10 == 0) deliverToOwner();
    }

    @Override
    protected InteractionResult mobInteract(Player player, InteractionHand hand) {
        if (!level().isClientSide && player.getUUID().equals(ownerUuid)) {
            ItemStack offered = player.getItemInHand(hand);
            if (!offered.isEmpty()) {
                long now = level().getGameTime();
                boolean confirmed = player.getUUID().equals(pendingOfferPlayer)
                        && now <= pendingOfferExpires && ItemStack.isSameItemSameTags(offered, pendingOffer);
                if (!confirmed) {
                    pendingOfferPlayer = player.getUUID();
                    pendingOffer = offered.copyWithCount(1);
                    pendingOfferExpires = now + 200;
                    player.sendSystemMessage(Component.translatable("message.alfheim_companion.offer_confirm",
                            offered.getHoverName()));
                    return InteractionResult.CONSUME;
                }

                ItemStack transferred = offered.copyWithCount(1);
                EquipmentSlot slot = Mob.getEquipmentSlotForItem(transferred);
                if (getItemBySlot(slot).isEmpty()) {
                    setItemSlot(slot, transferred);
                } else if (!inventory.addItem(transferred).isEmpty()) {
                    player.sendSystemMessage(Component.translatable("message.alfheim_companion.inventory_full"));
                    clearPendingOffer();
                    return InteractionResult.CONSUME;
                }
                if (!player.isCreative()) offered.shrink(1);
                player.sendSystemMessage(Component.translatable("message.alfheim_companion.offer_accepted",
                        transferred.getHoverName()));
                clearPendingOffer();
                return InteractionResult.CONSUME;
            }

            if (player.isShiftKeyDown() && inventory.getContainerSize() > 0) {
                for (int slot = 0; slot < inventory.getContainerSize(); slot++) {
                    ItemStack stored = inventory.getItem(slot);
                    if (!stored.isEmpty()) {
                        ItemStack returned = inventory.removeItemNoUpdate(slot);
                        if (!player.getInventory().add(returned)) player.drop(returned, false);
                        return InteractionResult.CONSUME;
                    }
                }
            }
            setMode(mode == CompanionMode.WAITING ? CompanionMode.FOLLOWING : CompanionMode.WAITING);
            player.sendSystemMessage(Component.translatable(
                    mode == CompanionMode.WAITING
                            ? "message.alfheim_companion.waiting"
                            : "message.alfheim_companion.following"));
            return InteractionResult.CONSUME;
        }
        return super.mobInteract(player, hand);
    }

    private void clearPendingOffer() {
        pendingOfferPlayer = null;
        pendingOffer = ItemStack.EMPTY;
        pendingOfferExpires = 0;
    }

    private void deliverToOwner() {
        ServerPlayer owner = resolveOwner();
        if (owner == null || owner.level() != level() || distanceToSqr(owner) > 9.0D) return;
        int remaining = deliveryCount;
        for (int slot = 0; slot < inventory.getContainerSize() && remaining > 0; slot++) {
            ItemStack stack = inventory.getItem(slot);
            if (stack.isEmpty() || !String.valueOf(ForgeRegistries.ITEMS.getKey(stack.getItem())).equals(deliveryItemId)) continue;
            ItemStack delivery = inventory.removeItem(slot, remaining);
            remaining -= delivery.getCount();
            if (!owner.getInventory().add(delivery)) owner.drop(delivery, false);
        }
        deliveryCount = remaining;
        if (remaining <= 0) {
            deliveryPending = false;
            deliveryItemId = "";
        }
    }

    @Override
    public boolean removeWhenFarAway(double distanceToClosestPlayer) {
        return false;
    }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        if (ownerUuid != null) tag.putUUID("Owner", ownerUuid);
        tag.putString("CompanionMode", mode.name());
        tag.put("Inventory", inventory.createTag());
        if (guardPosition != null) tag.putLong("GuardPosition", guardPosition.asLong());
        if (itemTaskTarget != null) tag.putUUID("ItemTaskTarget", itemTaskTarget);
        tag.putInt("ItemTaskCount", itemTaskCount);
        tag.putBoolean("ItemTaskFetch", itemTaskFetch);
        tag.putBoolean("DeliveryPending", deliveryPending);
        tag.putString("DeliveryItem", deliveryItemId);
        tag.putInt("DeliveryCount", deliveryCount);
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        if (tag.hasUUID("Owner")) ownerUuid = tag.getUUID("Owner");
        mode = CompanionMode.parse(tag.getString("CompanionMode"));
        inventory.fromTag(tag.getList("Inventory", net.minecraft.nbt.Tag.TAG_COMPOUND));
        guardPosition = tag.contains("GuardPosition", net.minecraft.nbt.Tag.TAG_LONG)
                ? BlockPos.of(tag.getLong("GuardPosition")) : null;
        itemTaskTarget = tag.hasUUID("ItemTaskTarget") ? tag.getUUID("ItemTaskTarget") : null;
        itemTaskCount = tag.getInt("ItemTaskCount");
        itemTaskFetch = tag.getBoolean("ItemTaskFetch");
        deliveryPending = tag.getBoolean("DeliveryPending");
        deliveryItemId = tag.getString("DeliveryItem");
        deliveryCount = tag.getInt("DeliveryCount");
    }

    @Override
    public Packet<ClientGamePacketListener> getAddEntityPacket() {
        return NetworkHooks.getEntitySpawningPacket(this);
    }
}

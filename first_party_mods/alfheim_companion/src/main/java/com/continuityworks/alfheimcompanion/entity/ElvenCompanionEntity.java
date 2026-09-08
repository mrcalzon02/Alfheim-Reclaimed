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
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraft.world.level.Level;
import net.minecraftforge.network.NetworkHooks;
import com.continuityworks.alfheimcompanion.service.EquipmentPolicy;
import com.continuityworks.alfheimcompanion.service.CompanionChunkTickets;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.world.Difficulty;
import net.minecraft.world.effect.MobEffectCategory;
import net.minecraft.world.item.alchemy.PotionUtils;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.MenuProvider;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.entity.player.Inventory;
import com.continuityworks.alfheimcompanion.menu.CompanionInventoryMenu;
import net.minecraftforge.network.NetworkHooks;

import java.util.UUID;

public final class ElvenCompanionEntity extends PathfinderMob implements MenuProvider {
    private static final EntityDataAccessor<Integer> DATA_MODE = SynchedEntityData.defineId(
            ElvenCompanionEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> DATA_NUTRITION = SynchedEntityData.defineId(
            ElvenCompanionEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> DATA_STAMINA = SynchedEntityData.defineId(
            ElvenCompanionEntity.class, EntityDataSerializers.INT);
    private UUID ownerUuid;
    private final SimpleContainer inventory = new SimpleContainer(CompanionInventoryMenu.COMPANION_SLOTS);
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
    private float exhaustion;
    private double lastBodyX;
    private double lastBodyZ;

    public ElvenCompanionEntity(EntityType<? extends PathfinderMob> type, Level level) {
        super(type, level);
        setPersistenceRequired();
    }

    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        entityData.define(DATA_MODE, CompanionMode.FOLLOWING.ordinal());
        entityData.define(DATA_NUTRITION, 20);
        entityData.define(DATA_STAMINA, 100);
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
        goalSelector.addGoal(1, new RetreatGoal(this));
        goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.1D, true));
        goalSelector.addGoal(3, new FollowOwnerGoal(this));
        goalSelector.addGoal(3, new ItemTaskGoal(this));
        goalSelector.addGoal(4, new GuardPositionGoal(this));
        goalSelector.addGoal(7, new LookAtPlayerGoal(this, Player.class, 8.0F));
        goalSelector.addGoal(8, new RandomLookAroundGoal(this));
        targetSelector.addGoal(1, new DefendLesseeTargetGoal(this));
    }

    public void bindOwner(UUID ownerUuid) {
        this.ownerUuid = ownerUuid;
    }

    public UUID ownerUuid() {
        return ownerUuid;
    }

    public CompanionMode mode() {
        int ordinal = entityData.get(DATA_MODE);
        CompanionMode[] values = CompanionMode.values();
        return ordinal >= 0 && ordinal < values.length ? values[ordinal] : CompanionMode.FOLLOWING;
    }

    public SimpleContainer inventory() {
        return inventory;
    }

    public int nutrition() { return entityData.get(DATA_NUTRITION); }
    public int stamina() { return entityData.get(DATA_STAMINA); }

    public void setMode(CompanionMode mode) {
        entityData.set(DATA_MODE, mode.ordinal());
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
        if (!level().isClientSide) tickSurvivalNeeds();
        if (!level().isClientSide && tickCount % 100 == 0 && getServer() != null) {
            CompanionSavedData.get(getServer()).updateLocation(
                    level().dimension().location().toString(), blockPosition());
        }
        if (!level().isClientSide && tickCount % 20 == 0) CompanionChunkTickets.update(this);
        if (!level().isClientSide && deliveryPending && tickCount % 10 == 0) deliverToOwner();
    }

    private void tickSurvivalNeeds() {
        ServerPlayer owner = resolveOwner();
        boolean survivalRules = level().getDifficulty() != Difficulty.PEACEFUL
                && (owner == null || !owner.isCreative());
        double moved = Math.sqrt((getX() - lastBodyX) * (getX() - lastBodyX)
                + (getZ() - lastBodyZ) * (getZ() - lastBodyZ));
        lastBodyX = getX();
        lastBodyZ = getZ();

        if (!survivalRules) {
            if (tickCount % 100 == 0) {
                entityData.set(DATA_NUTRITION, Math.min(20, nutrition() + 1));
                entityData.set(DATA_STAMINA, Math.min(100, stamina() + 5));
            }
            return;
        }

        float movementCost = (float) Math.min(1.0D, moved * (isSprinting() || mode() == CompanionMode.RETREATING ? 0.10D : 0.01D));
        float activityCost = switch (mode()) {
            case WORKING -> 0.004F;
            case DEFENDING, RETREATING -> 0.01F;
            default -> 0.0F;
        };
        exhaustion += movementCost + activityCost;
        while (exhaustion >= 4.0F) {
            exhaustion -= 4.0F;
            entityData.set(DATA_NUTRITION, Math.max(0, nutrition() - 1));
        }

        if (tickCount % 20 == 0) {
            int staminaChange = moved > 0.08D || mode() == CompanionMode.WORKING
                    || mode() == CompanionMode.DEFENDING || mode() == CompanionMode.RETREATING ? -1 : 0;
            if ((mode() == CompanionMode.WAITING || mode() == CompanionMode.GUARDING) && nutrition() > 6) staminaChange = 2;
            if (nutrition() <= 4) staminaChange--;
            entityData.set(DATA_STAMINA, Math.max(0, Math.min(100, stamina() + staminaChange)));
        }
        if (nutrition() <= 12 && tickCount % 40 == 0) tryEat();
        if (getHealth() < getMaxHealth() * 0.5F && tickCount % 40 == 0) tryDrinkBeneficialPotion();
        if (tickCount % 200 == 0 && getServer() != null) {
            int moodChange = nutrition() <= 4 || stamina() <= 10 ? -2
                    : ((mode() == CompanionMode.WAITING || mode() == CompanionMode.GUARDING) && stamina() > 70 ? 1 : 0);
            if (moodChange != 0) CompanionSavedData.get(getServer()).adjustMood(moodChange, level().getGameTime());
        }
    }

    private void tryEat() {
        for (int slot = 0; slot < inventory.getContainerSize(); slot++) {
            ItemStack stack = inventory.getItem(slot);
            var food = stack.getFoodProperties(this);
            if (stack.isEmpty() || food == null) continue;
            entityData.set(DATA_NUTRITION, Math.min(20, nutrition() + food.getNutrition()));
            inventory.removeItem(slot, 1);
            level().playSound(null, blockPosition(), SoundEvents.GENERIC_EAT, SoundSource.NEUTRAL, 0.8F, 1.0F);
            if (getServer() != null) CompanionSavedData.get(getServer()).adjustMood(2, level().getGameTime());
            return;
        }
    }

    private void tryDrinkBeneficialPotion() {
        for (int slot = 0; slot < inventory.getContainerSize(); slot++) {
            ItemStack stack = inventory.getItem(slot);
            if (!stack.is(Items.POTION)) continue;
            var effects = PotionUtils.getMobEffects(stack).stream()
                    .filter(effect -> effect.getEffect().getCategory() == MobEffectCategory.BENEFICIAL).toList();
            if (effects.isEmpty()) continue;
            effects.forEach(effect -> addEffect(new net.minecraft.world.effect.MobEffectInstance(effect)));
            inventory.removeItem(slot, 1);
            inventory.addItem(new ItemStack(Items.GLASS_BOTTLE));
            level().playSound(null, blockPosition(), SoundEvents.GENERIC_DRINK, SoundSource.NEUTRAL, 0.8F, 1.0F);
            return;
        }
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
                java.util.Optional<EquipmentSlot> understood = EquipmentPolicy.understoodSlot(transferred);
                if (understood.isPresent() && getItemBySlot(understood.get()).isEmpty()) {
                    setItemSlot(understood.get(), transferred);
                } else if (!inventory.addItem(transferred).isEmpty()) {
                    player.sendSystemMessage(Component.translatable("message.alfheim_companion.inventory_full"));
                    clearPendingOffer();
                    return InteractionResult.CONSUME;
                }
                if (!player.isCreative()) offered.shrink(1);
                player.sendSystemMessage(Component.translatable("message.alfheim_companion.offer_accepted",
                        transferred.getHoverName()));
                if (understood.isEmpty() && !transferred.isEdible() && !transferred.is(Items.POTION)) {
                    player.sendSystemMessage(Component.literal("I can carry this, but I do not know how to use it safely."));
                }
                clearPendingOffer();
                return InteractionResult.CONSUME;
            }

            if (player.isShiftKeyDown() && inventory.getContainerSize() > 0) {
                setMode(mode() == CompanionMode.WAITING ? CompanionMode.FOLLOWING : CompanionMode.WAITING);
                player.sendSystemMessage(Component.translatable(mode() == CompanionMode.WAITING
                        ? "message.alfheim_companion.waiting" : "message.alfheim_companion.following"));
                return InteractionResult.CONSUME;
            }
            if (player instanceof ServerPlayer serverPlayer) {
                NetworkHooks.openScreen(serverPlayer, this, buffer -> buffer.writeVarInt(getId()));
            }
            return InteractionResult.CONSUME;
        }
        return super.mobInteract(player, hand);
    }

    @Override
    public Component getDisplayName() {
        return getCustomName() == null ? Component.literal("Elven Companion") : getCustomName();
    }

    @Override
    public AbstractContainerMenu createMenu(int containerId, Inventory inventory, Player player) {
        if (!player.getUUID().equals(ownerUuid)) return null;
        return new CompanionInventoryMenu(containerId, inventory, this);
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
        tag.putString("CompanionMode", mode().name());
        tag.put("Inventory", inventory.createTag());
        if (guardPosition != null) tag.putLong("GuardPosition", guardPosition.asLong());
        if (itemTaskTarget != null) tag.putUUID("ItemTaskTarget", itemTaskTarget);
        tag.putInt("ItemTaskCount", itemTaskCount);
        tag.putBoolean("ItemTaskFetch", itemTaskFetch);
        tag.putBoolean("DeliveryPending", deliveryPending);
        tag.putString("DeliveryItem", deliveryItemId);
        tag.putInt("DeliveryCount", deliveryCount);
        tag.putInt("Nutrition", nutrition());
        tag.putInt("Stamina", stamina());
        tag.putFloat("Exhaustion", exhaustion);
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        if (tag.hasUUID("Owner")) ownerUuid = tag.getUUID("Owner");
        setMode(CompanionMode.parse(tag.getString("CompanionMode")));
        inventory.fromTag(tag.getList("Inventory", net.minecraft.nbt.Tag.TAG_COMPOUND));
        guardPosition = tag.contains("GuardPosition", net.minecraft.nbt.Tag.TAG_LONG)
                ? BlockPos.of(tag.getLong("GuardPosition")) : null;
        itemTaskTarget = tag.hasUUID("ItemTaskTarget") ? tag.getUUID("ItemTaskTarget") : null;
        itemTaskCount = tag.getInt("ItemTaskCount");
        itemTaskFetch = tag.getBoolean("ItemTaskFetch");
        deliveryPending = tag.getBoolean("DeliveryPending");
        deliveryItemId = tag.getString("DeliveryItem");
        deliveryCount = tag.getInt("DeliveryCount");
        entityData.set(DATA_NUTRITION, tag.contains("Nutrition") ? Math.max(0, Math.min(20, tag.getInt("Nutrition"))) : 20);
        entityData.set(DATA_STAMINA, tag.contains("Stamina") ? Math.max(0, Math.min(100, tag.getInt("Stamina"))) : 100);
        exhaustion = Math.max(0.0F, Math.min(4.0F, tag.getFloat("Exhaustion")));
    }

    @Override
    public Packet<ClientGamePacketListener> getAddEntityPacket() {
        return NetworkHooks.getEntitySpawningPacket(this);
    }
}

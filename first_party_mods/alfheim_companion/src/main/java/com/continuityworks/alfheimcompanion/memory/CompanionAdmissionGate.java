package com.continuityworks.alfheimcompanion.memory;

import java.util.UUID;

/**
 * Short-lived admission for the first-party companion currently being inserted by Forge.
 * A failed insertion must not change the serialized companion UUID/owner. Already-committed
 * identities remain valid during legitimate save reloads and dimension transfers.
 */
public final class CompanionAdmissionGate {
    private UUID pendingEntity;
    private UUID pendingOwner;

    public boolean begin(UUID entity, UUID owner) {
        if (entity == null || owner == null || pendingEntity != null) return false;
        pendingEntity = entity;
        pendingOwner = owner;
        return true;
    }

    public boolean allows(UUID entity, UUID owner, UUID committedEntity, UUID committedOwner) {
        if (entity == null || owner == null) return false;
        return (entity.equals(pendingEntity) && owner.equals(pendingOwner))
                || (entity.equals(committedEntity) && owner.equals(committedOwner));
    }

    public void end(UUID entity, UUID owner) {
        if (entity == null || owner == null
                || !entity.equals(pendingEntity) || !owner.equals(pendingOwner))
            throw new IllegalStateException("No matching companion admission reservation");
        pendingEntity = null;
        pendingOwner = null;
    }
}

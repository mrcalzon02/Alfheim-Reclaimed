package com.continuityworks.alfheimgolems.order;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceLocation;

import java.util.Objects;
import java.util.UUID;

/**
 * Server-created reference to one face of one loaded inventory.
 *
 * <p>The UUID is safe to send to a client after authorization. The position is retained only on
 * the server and must be revalidated before every mutation.
 */
public record EndpointRef(UUID id, ResourceLocation dimension, BlockPos position, Direction face) {
    public EndpointRef {
        Objects.requireNonNull(id, "id");
        Objects.requireNonNull(dimension, "dimension");
        Objects.requireNonNull(position, "position");
        Objects.requireNonNull(face, "face");
        position = position.immutable();
    }
}

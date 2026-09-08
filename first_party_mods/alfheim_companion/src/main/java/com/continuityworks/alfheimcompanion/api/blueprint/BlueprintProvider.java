package com.continuityworks.alfheimcompanion.api.blueprint;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;

import java.util.List;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;

/**
 * Versioned Java endpoint implemented by Continuity Works. All values crossing this boundary are
 * immutable snapshots; implementations may compute off-thread but must not access a live Level there.
 */
public interface BlueprintProvider {
    int API_VERSION = 1;

    enum Capability { CATALOG, SITE_ANALYSIS, GENERATION, VALIDATION, MATERIAL_MANIFEST, PREVIEW }

    int apiVersion();

    Set<Capability> capabilities();

    CompletableFuture<BlueprintProposal> generate(BlueprintRequest request);

    BlueprintValidation validate(BlueprintProposal proposal, BlueprintWorldSnapshot worldSnapshot);

    default void cancel(UUID requestId) {}

    record BlueprintRequest(
            UUID requestId,
            UUID companionUuid,
            UUID ownerUuid,
            String dimensionId,
            String purpose,
            BlockPos preferredOrigin,
            Direction preferredFacing,
            Bounds maximumBounds,
            List<MaterialAmount> availableMaterials,
            List<SiteCandidate> candidates,
            Set<String> permittedStyles
    ) {
        public BlueprintRequest {
            availableMaterials = List.copyOf(availableMaterials);
            candidates = List.copyOf(candidates);
            permittedStyles = Set.copyOf(permittedStyles);
        }
    }

    record BlueprintProposal(
            UUID blueprintId,
            int formatVersion,
            String integrityHash,
            BlockPos origin,
            Direction facing,
            Bounds bounds,
            List<Placement> placements,
            List<MaterialAmount> materials,
            List<String> warnings
    ) {
        public BlueprintProposal {
            placements = List.copyOf(placements);
            materials = List.copyOf(materials);
            warnings = List.copyOf(warnings);
        }
    }

    record BlueprintValidation(boolean valid, List<String> errors, List<String> warnings) {
        public BlueprintValidation {
            errors = List.copyOf(errors);
            warnings = List.copyOf(warnings);
        }
    }

    record BlueprintWorldSnapshot(String dimensionId, BlockPos origin, Bounds bounds,
                                  List<BlockSample> blocks, Set<Long> protectedPositions) {
        public BlueprintWorldSnapshot {
            blocks = List.copyOf(blocks);
            protectedPositions = Set.copyOf(protectedPositions);
        }
    }

    record Bounds(int x, int y, int z) {}
    record MaterialAmount(String itemId, int count) {}
    record SiteCandidate(String key, BlockPos origin, Direction facing, int suitability) {}
    record Placement(BlockPos relativePosition, String blockStateId) {}
    record BlockSample(BlockPos relativePosition, String blockStateId) {}
}

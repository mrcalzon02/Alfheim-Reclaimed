package com.continuityworks.alfheimcompanion.worldgen;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.PoolElementStructurePiece;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureType;
import net.minecraft.world.level.levelgen.structure.pools.StructurePoolElement;
import net.minecraft.world.level.levelgen.structure.pools.StructureTemplatePool;
import java.util.Arrays;
import java.util.Optional;

/**
 * Terrain-hosted single-piece Void ruins. Unlike a jigsaw projected to
 * WORLD_SURFACE_WG, an empty column does not get mistaken for the dimension floor.
 * The nine samples examine actual generated noise columns without chunk loads.
 *
 * No fake foundations, no downward relocation, no additional rescue islands:
 * insufficient solid backing returns Optional.empty() before structure creation.
 */
public final class VoidSurfaceStructure extends Structure {
    public static final Codec<VoidSurfaceStructure> CODEC = RecordCodecBuilder.create(i -> i.group(
        settingsCodec(i),
        ResourceLocation.CODEC.fieldOf("template").forGetter(s -> s.template),
        Codec.INT.fieldOf("ground").forGetter(s -> s.ground),
        Codec.INT.fieldOf("min_surface_y").forGetter(s -> s.minSurfaceY),
        Codec.INT.fieldOf("max_surface_y").forGetter(s -> s.maxSurfaceY),
        Codec.INT.fieldOf("min_support").forGetter(s -> s.minSupport),
        Codec.INT.fieldOf("sample_radius").forGetter(s -> s.radius),
        Codec.INT.fieldOf("max_relief").forGetter(s -> s.maxRelief),
        Codec.INT.fieldOf("solid_depth").forGetter(s -> s.solidDepth),
        Codec.INT.fieldOf("support_offset_x").forGetter(s -> s.offsetX),
        Codec.INT.fieldOf("support_offset_z").forGetter(s -> s.offsetZ)
    ).apply(i, VoidSurfaceStructure::new));

    private final ResourceLocation template;
    private final int ground, minSurfaceY, maxSurfaceY, minSupport, radius;
    private final int maxRelief, solidDepth, offsetX, offsetZ;

    public VoidSurfaceStructure(StructureSettings settings, ResourceLocation template,
            int ground, int minSurfaceY, int maxSurfaceY, int minSupport,
            int radius, int maxRelief, int solidDepth, int offsetX, int offsetZ) {
        super(settings);
        if (minSurfaceY < 64 || maxSurfaceY > 110 || minSurfaceY > maxSurfaceY
                || minSupport < 1 || minSupport > 9 || radius < 1 || radius > 16
                || maxRelief < 0 || maxRelief > 16 || solidDepth < 1
                || solidDepth > 32 || Math.abs(offsetX) > 32 || Math.abs(offsetZ) > 32)
            throw new IllegalArgumentException("Invalid Void terrain support configuration for " + template);
        this.template = template;
        this.ground = ground;
        this.minSurfaceY = minSurfaceY;
        this.maxSurfaceY = maxSurfaceY;
        this.minSupport = minSupport;
        this.radius = radius;
        this.maxRelief = maxRelief;
        this.solidDepth = solidDepth;
        this.offsetX = offsetX;
        this.offsetZ = offsetZ;
    }

    @Override
    protected Optional<GenerationStub> findGenerationPoint(GenerationContext context) {
        final int centreX = context.chunkPos().getMiddleBlockX();
        final int centreZ = context.chunkPos().getMiddleBlockZ();
        final Rotation rotation = Rotation.values()[context.random().nextInt(4)];

        // Same quarter-turn ordering as HarborGeometry: (x,z) -> (-z,x).
        int dx = offsetX, dz = offsetZ;
        for (int turn = 0; turn < rotation.ordinal(); turn++) {
            int oldX = dx;
            dx = -dz;
            dz = oldX;
        }
        final int supportX = centreX + dx;
        final int supportZ = centreZ + dz;

        // Nine fixed probes. This is bounded work and uses base terrain, not
        // loaded chunks. A structure on an empty column is rejected.
        int[] supported = new int[9];
        int count = 0;
        for (int ix = -1; ix <= 1; ix++) for (int iz = -1; iz <= 1; iz++) {
            int px = supportX + ix * radius;
            int pz = supportZ + iz * radius;
            int surface = context.chunkGenerator().getBaseHeight(px, pz,
                Heightmap.Types.WORLD_SURFACE_WG, context.heightAccessor(), context.randomState());
            if (surface < minSurfaceY || surface > maxSurfaceY) continue;
            var column = context.chunkGenerator().getBaseColumn(px, pz,
                context.heightAccessor(), context.randomState());
            boolean solid = true;
            for (int y = surface - 1; y >= surface - solidDepth; y--) {
                var block = column.getBlock(y);
                if (block.isAir() || !block.getFluidState().isEmpty()) {
                    solid = false;
                    break;
                }
            }
            if (solid) supported[count++] = surface;
        }
        if (count < minSupport) return Optional.empty();

        Arrays.sort(supported, 0, count);
        final int surfaceY = supported[count / 2];
        int near = 0;
        for (int i = 0; i < count; i++) {
            if (Math.abs(supported[i] - surfaceY) <= maxRelief) near++;
        }
        if (near < minSupport) return Optional.empty();

        final int originY = surfaceY - ground;
        final var manager = context.structureTemplateManager();
        final var element = StructurePoolElement.single(template.toString())
            .apply(StructureTemplatePool.Projection.RIGID);

        // Rotated single-piece templates are centred around the accepted
        // candidate instead of swinging off the edge of the selected chunk.
        final BlockPos provisional = new BlockPos(centreX, originY, centreZ);
        BoundingBox initial = element.getBoundingBox(manager, provisional, rotation);
        BlockPos origin = provisional.offset(centreX - (initial.minX() + initial.maxX()) / 2,
                                            0, centreZ - (initial.minZ() + initial.maxZ()) / 2);
        BoundingBox finalBox = element.getBoundingBox(manager, origin, rotation);

        return Optional.of(new GenerationStub(new BlockPos(centreX, surfaceY, centreZ),
            builder -> builder.addPiece(new PoolElementStructurePiece(
                manager, element, origin, 1, rotation, finalBox))));
    }

    @Override
    public StructureType<?> type() {
        return ModHarborStructures.VOID_SURFACE.get();
    }
}

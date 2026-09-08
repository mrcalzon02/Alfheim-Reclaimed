package com.continuityworks.leyworks;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.TagKey;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.List;

/**
 * The live conduit node.
 *
 * <p><b>Modified beacon-pyramid rules.</b> Vanilla wants a four-tier pyramid of a fixed block
 * list beneath a beacon and then grants effects globally. This reads the same shape but changes
 * what it is for: the tier does not choose an effect, it chooses <em>reach</em> -- node-to-node
 * projection distance and aura radius -- exactly as the design specifies, "Pyramid tier
 * determines node-to-node range and aura radius". Any full course of a block in the
 * alfheim_leyworks:pyramid_base tag counts, so the pack decides its own masonry instead of
 * inheriting iron and diamond.
 *
 * <p><b>Six-direction projection.</b> The node projects north, south, east, west, up and down.
 * Air and blocks tagged alfheim_leyworks:beam_transmits carry it; anything else stops it. That
 * is what lets architecture mask unused faces instead of needing a different block per shape.
 *
 * <p>Generated networks are dormant by construction, so nothing here grants a free payload: a
 * node only reaches tier 1 or better once a player has actually built the pyramid under it.
 */
public class LeyConduitNodeBlockEntity extends BlockEntity {

    /** Blocks a projection passes through. Air is always allowed and is not in the tag. */
    public static final TagKey<Block> TRANSMITS =
            BlockTags.create(new ResourceLocation(Leyworks.MOD_ID, "beam_transmits"));

    /** Blocks that count as a pyramid course. */
    public static final TagKey<Block> PYRAMID =
            BlockTags.create(new ResourceLocation(Leyworks.MOD_ID, "pyramid_base"));

    /** Registered by KubeJS in 23_leyline_effects.js; looked up by id so the two stay decoupled. */
    private static final ResourceLocation PRESENCE =
            new ResourceLocation("alfheim", "leyline_presence");

    private static final int MAX_TIER = 4;
    private static final int RANGE_PER_TIER = 12;
    private static final int RECHECK_TICKS = 80;

    private int tier;
    private int cooldown;

    public LeyConduitNodeBlockEntity(BlockPos pos, BlockState state) {
        super(Leyworks.NODE_ENTITY.get(), pos, state);
    }

    public int tier() {
        return tier;
    }

    /** Aura radius and node-to-node reach both scale with the pyramid beneath. */
    public int reach() {
        return tier * RANGE_PER_TIER;
    }

    public static void tick(Level level, BlockPos pos, BlockState state,
                            LeyConduitNodeBlockEntity be) {
        if (level.isClientSide) {
            be.clientParticles(level, pos);
            return;
        }
        if (--be.cooldown > 0) {
            return;
        }
        be.cooldown = RECHECK_TICKS;
        int found = readPyramid(level, pos);
        if (found != be.tier) {
            be.tier = found;
            be.setChanged();
        }
        if (be.tier > 0) {
            be.applyAura((ServerLevel) level, pos);
        }
    }

    /**
     * Count complete pyramid courses beneath the node: vanilla's shape, our own block list.
     * Course n is a (2n+1) square centred under the node at depth n.
     */
    private static int readPyramid(Level level, BlockPos pos) {
        int found = 0;
        for (int layer = 1; layer <= MAX_TIER; layer++) {
            int y = pos.getY() - layer;
            if (y < level.getMinBuildHeight()) {
                break;
            }
            boolean complete = true;
            for (int dx = -layer; dx <= layer && complete; dx++) {
                for (int dz = -layer; dz <= layer; dz++) {
                    BlockState s = level.getBlockState(
                            new BlockPos(pos.getX() + dx, y, pos.getZ() + dz));
                    if (!s.is(PYRAMID)) {
                        complete = false;
                        break;
                    }
                }
            }
            if (!complete) {
                break;
            }
            found = layer;
        }
        return found;
    }

    /**
     * How far the projection travels along one axis before something opaque stops it. Public so
     * a renderer or a probe can ask without duplicating the transmission rule.
     */
    public int projectionLength(Level level, BlockPos pos, Direction dir) {
        int limit = Math.max(1, reach());
        BlockPos.MutableBlockPos cursor = pos.mutable();
        for (int i = 1; i <= limit; i++) {
            cursor.set(pos.getX(), pos.getY(), pos.getZ());
            cursor.move(dir, i);
            BlockState s = level.getBlockState(cursor);
            if (!s.isAir() && !s.is(TRANSMITS)) {
                return i - 1;
            }
        }
        return limit;
    }

    /** Leyline Presence to every player standing in the field. */
    private void applyAura(ServerLevel level, BlockPos pos) {
        MobEffect presence = ForgeRegistries.MOB_EFFECTS.getValue(PRESENCE);
        if (presence == null) {
            // KubeJS did not register it. The node still projects; it just cannot buff.
            return;
        }
        AABB field = new AABB(pos).inflate(reach());
        List<Player> players = level.getEntitiesOfClass(Player.class, field);
        for (Player p : players) {
            // Refreshed longer than the recheck interval so it never flickers between ticks,
            // and re-applied rather than stacked.
            p.addEffect(new MobEffectInstance(presence, RECHECK_TICKS * 2, 0, true, false, true));
        }
    }

    /**
     * The visible channel: motes travelling outward along every open axis.
     *
     * <p>This is the "custom particle effects" half of the design's beam. A true beacon-style
     * rendered light column is a separate client renderer; particles carry the same information
     * -- which faces are open, and how far the projection reaches -- and cost the server nothing.
     */
    private void clientParticles(Level level, BlockPos pos) {
        if (level.getGameTime() % 4 != 0) {
            return;
        }
        double cx = pos.getX() + 0.5;
        double cy = pos.getY() + 0.5;
        double cz = pos.getZ() + 0.5;
        for (Direction dir : Direction.values()) {
            int len = projectionLength(level, pos, dir);
            for (int i = 1; i <= len; i++) {
                if ((level.getGameTime() / 4 + i) % 3 != 0) {
                    continue;
                }
                level.addParticle(ParticleTypes.END_ROD,
                        cx + dir.getStepX() * i,
                        cy + dir.getStepY() * i,
                        cz + dir.getStepZ() * i,
                        0.0D, 0.0D, 0.0D);
            }
        }
    }

    @Override
    protected void saveAdditional(CompoundTag tag) {
        super.saveAdditional(tag);
        tag.putInt("Tier", tier);
    }

    @Override
    public void load(CompoundTag tag) {
        super.load(tag);
        tier = tag.getInt("Tier");
    }
}

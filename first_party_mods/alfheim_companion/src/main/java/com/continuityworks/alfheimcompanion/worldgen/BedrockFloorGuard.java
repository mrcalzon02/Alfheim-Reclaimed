package com.continuityworks.alfheimcompanion.worldgen;

import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.TagKey;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.chunk.LevelChunk;
import net.minecraftforge.event.level.ChunkEvent;

/** Finite floor repair after generation, including already saved chunks.
 * Only Alfheim's minimum build layer is touched; Void columns stay open.
 * Direct chunk writes do not request neighbours or schedule block ticks.
 */
public final class BedrockFloorGuard {
    private static final ResourceLocation HOME = new ResourceLocation("mythicbotany", "alfheim");
    private static final TagKey<Biome> VOID = TagKey.create(Registries.BIOME,
        new ResourceLocation("alfheim", "void_margins"));

    public static void onChunkLoad(ChunkEvent.Load event) {
        if (!(event.getLevel() instanceof ServerLevel level)
                || !level.dimension().location().equals(HOME)
                || !(event.getChunk() instanceof LevelChunk chunk)) return;
        int y = chunk.getMinBuildHeight();
        BlockPos.MutableBlockPos position = new BlockPos.MutableBlockPos();
        int baseX = chunk.getPos().getMinBlockX(), baseZ = chunk.getPos().getMinBlockZ();
        for (int z = 0; z < 16; z++) for (int x = 0; x < 16; x++) {
            // Alfheim's horizontal biome claims are defined at surface altitude.
            if (chunk.getNoiseBiome((baseX+x)>>2, 16, (baseZ+z)>>2).is(VOID)) continue;
            position.set(baseX+x, y, baseZ+z);
            if (!chunk.getBlockState(position).is(Blocks.BEDROCK))
                chunk.setBlockState(position, Blocks.BEDROCK.defaultBlockState(), false);
        }
    }

    private BedrockFloorGuard() {}
}

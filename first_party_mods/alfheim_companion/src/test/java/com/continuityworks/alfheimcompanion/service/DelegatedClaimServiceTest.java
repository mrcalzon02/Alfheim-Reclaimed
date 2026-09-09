package com.continuityworks.alfheimcompanion.service;

import com.continuityworks.alfheimcompanion.brain.ClaimDistrictDecision;
import com.continuityworks.alfheimcompanion.brain.ClaimDistrictSnapshot;
import com.continuityworks.alfheimcompanion.brain.RuleBasedTinyBrainEngine;
import net.minecraft.world.level.ChunkPos;
import org.junit.jupiter.api.Test;

import java.util.HashSet;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;

class DelegatedClaimServiceTest {
    @Test
    void districtIsExactlyFiveByFiveAndStartsAtCenter() {
        ChunkPos center = new ChunkPos(10, -4);
        var order = DelegatedClaimService.districtOrder(center);
        assertEquals(25, order.size());
        assertEquals(25, new HashSet<>(order).size());
        assertEquals(center, order.get(0));
        assertTrue(order.stream().allMatch(position -> Math.max(Math.abs(position.x - center.x),
                Math.abs(position.z - center.z)) <= 2));
    }

    @Test
    void deterministicInferenceKeepsCloseValuesAndMovesForClearGain() {
        RuleBasedTinyBrainEngine engine = new RuleBasedTinyBrainEngine();
        ClaimDistrictSnapshot close = snapshot(60, 67);
        ClaimDistrictSnapshot better = snapshot(40, 70);
        assertEquals(ClaimDistrictDecision.Choice.KEEP_DISTRICT,
                engine.chooseClaimDistrict(close).join().choice());
        assertEquals(ClaimDistrictDecision.Choice.RELOCATE_DISTRICT,
                engine.chooseClaimDistrict(better).join().choice());
    }

    private static ClaimDistrictSnapshot snapshot(int current, int candidate) {
        return new ClaimDistrictSnapshot(1, UUID.randomUUID(), "minecraft:overworld",
                new ChunkPos(0, 0), new ChunkPos(8, 8), current, candidate,
                "balanced", "established", "more open chunks");
    }
}

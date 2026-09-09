package com.continuityworks.alfheimgolems.config;

import net.minecraftforge.common.ForgeConfigSpec;

/** Bounded common-server defaults. Values do not grant capabilities; they only reduce budgets. */
public final class GolemConfig {
    public static final ForgeConfigSpec SPEC;
    public static final ForgeConfigSpec.IntValue DECISIONS_PER_TICK;
    public static final ForgeConfigSpec.IntValue MUTATION_INTERVAL_TICKS;
    public static final ForgeConfigSpec.IntValue MAX_GOLEMS_PER_OWNER;
    public static final ForgeConfigSpec.IntValue MAX_ENDPOINTS_PER_ORDER;
    public static final ForgeConfigSpec.IntValue MAX_QUEUED_CRAFTS;
    public static final ForgeConfigSpec.IntValue MAX_NAVIGATION_RANGE;
    public static final ForgeConfigSpec.IntValue SENTINEL_LIFETIME_TICKS;
    public static final ForgeConfigSpec.BooleanValue WORK_EXECUTION_ENABLED;
    public static final ForgeConfigSpec.BooleanValue SENTINEL_SUMMONING_ENABLED;

    static {
        ForgeConfigSpec.Builder builder = new ForgeConfigSpec.Builder();
        builder.comment("Global safety and scheduling bounds for Alfheim Golems.").push("limits");
        DECISIONS_PER_TICK = builder
                .comment("Maximum lightweight golem decisions scheduled in one server tick.")
                .defineInRange("decisionsPerTick", 64, 1, 512);
        MUTATION_INTERVAL_TICKS = builder
                .comment("Minimum ticks between inventory mutations by one golem.")
                .defineInRange("mutationIntervalTicks", 10, 1, 1200);
        MAX_GOLEMS_PER_OWNER = builder
                .defineInRange("maxGolemsPerOwner", 64, 1, 256);
        MAX_ENDPOINTS_PER_ORDER = builder
                .defineInRange("maxEndpointsPerOrder", 16, 2, 64);
        MAX_QUEUED_CRAFTS = builder
                .defineInRange("maxQueuedCrafts", 64, 1, 4096);
        MAX_NAVIGATION_RANGE = builder
                .comment("Maximum same-dimension route length. This never loads a chunk.")
                .defineInRange("maxNavigationRange", 64, 8, 256);
        SENTINEL_LIFETIME_TICKS = builder
                .comment("Temporary combat summon lifetime; 2400 ticks is 120 seconds.")
                .defineInRange("sentinelLifetimeTicks", 2400, 200, 12000);
        builder.pop();

        builder.comment("Emergency feature switches. Disabling work never deletes saved orders.")
                .push("safety");
        WORK_EXECUTION_ENABLED = builder.define("workExecutionEnabled", true);
        SENTINEL_SUMMONING_ENABLED = builder.define("sentinelSummoningEnabled", true);
        builder.pop();
        SPEC = builder.build();
    }

    private GolemConfig() {}
}

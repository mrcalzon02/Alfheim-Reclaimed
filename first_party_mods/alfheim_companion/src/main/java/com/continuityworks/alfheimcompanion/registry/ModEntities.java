package com.continuityworks.alfheimcompanion.registry;

import com.continuityworks.alfheimcompanion.AlfheimCompanion;
import com.continuityworks.alfheimcompanion.entity.ElvenCompanionEntity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public final class ModEntities {
    public static final DeferredRegister<EntityType<?>> REGISTRY =
            DeferredRegister.create(ForgeRegistries.ENTITY_TYPES, AlfheimCompanion.MOD_ID);

    public static final RegistryObject<EntityType<ElvenCompanionEntity>> ELVEN_COMPANION = REGISTRY.register(
            "elven_companion",
            () -> EntityType.Builder.of(ElvenCompanionEntity::new, MobCategory.CREATURE)
                    .sized(0.6F, 1.8F)
                    .clientTrackingRange(10)
                    .updateInterval(2)
                    .build(AlfheimCompanion.MOD_ID + ":elven_companion")
    );

    public static final RegistryObject<EntityType<com.continuityworks.alfheimcompanion.society.ElvenCitizenEntity>> ELVEN_CITIZEN = REGISTRY.register(
        "elven_citizen",()->EntityType.Builder.of(com.continuityworks.alfheimcompanion.society.ElvenCitizenEntity::new,MobCategory.CREATURE)
            .sized(.6F,1.95F).clientTrackingRange(10).build(AlfheimCompanion.MOD_ID+":elven_citizen"));
    private ModEntities() {}
}

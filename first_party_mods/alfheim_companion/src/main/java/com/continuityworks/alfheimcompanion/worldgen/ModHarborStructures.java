package com.continuityworks.alfheimcompanion.worldgen;

import com.continuityworks.alfheimcompanion.AlfheimCompanion;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.levelgen.structure.StructureType;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.RegistryObject;

public final class ModHarborStructures {
    public static final DeferredRegister<StructureType<?>> REGISTRY=DeferredRegister.create(Registries.STRUCTURE_TYPE,AlfheimCompanion.MOD_ID);
    public static final RegistryObject<StructureType<HarborStructure>> HARBOR=REGISTRY.register("shoreline_harbor",()->()->HarborStructure.CODEC);
    private ModHarborStructures() {}
}

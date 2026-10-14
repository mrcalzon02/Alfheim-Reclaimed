package com.continuityworks.alfheimcompanion.worldgen;

import com.continuityworks.alfheimcompanion.AlfheimCompanion;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.levelgen.structure.StructureType;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.RegistryObject;

public final class ModHarborStructures {
    public static final DeferredRegister<StructureType<?>> REGISTRY=DeferredRegister.create(Registries.STRUCTURE_TYPE,AlfheimCompanion.MOD_ID);
    public static final RegistryObject<StructureType<HarborStructure>> HARBOR=REGISTRY.register("shoreline_harbor",()->()->HarborStructure.CODEC);
    // Source-only until a rebuilt companion JAR is distributed. Never switch
    // worldgen JSON to this type before that JAR has been installed.
    public static final RegistryObject<StructureType<VoidSurfaceStructure>> VOID_SURFACE =
        REGISTRY.register("void_surface", () -> () -> VoidSurfaceStructure.CODEC);
    private ModHarborStructures() {}
}

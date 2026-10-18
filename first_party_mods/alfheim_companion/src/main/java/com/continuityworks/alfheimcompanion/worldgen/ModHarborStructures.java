package com.continuityworks.alfheimcompanion.worldgen;

import com.continuityworks.alfheimcompanion.AlfheimCompanion;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.levelgen.structure.StructureType;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.RegistryObject;

public final class ModHarborStructures {
    public static final DeferredRegister<net.minecraft.world.level.levelgen.structure.placement.StructurePlacementType<?>> PLACEMENTS=
        DeferredRegister.create(Registries.STRUCTURE_PLACEMENT,AlfheimCompanion.MOD_ID);
    public static final RegistryObject<net.minecraft.world.level.levelgen.structure.placement.StructurePlacementType<DistrictRingPlacement>> DISTRICT_RINGS=
        PLACEMENTS.register("district_rings",()->()->DistrictRingPlacement.CODEC);
    public static final RegistryObject<net.minecraft.world.level.levelgen.structure.placement.StructurePlacementType<LabyrinthRingPlacement>> LABYRINTH_RINGS=
        PLACEMENTS.register("labyrinth_rings",()->()->LabyrinthRingPlacement.CODEC);
    public static final DeferredRegister<StructureType<?>> REGISTRY=DeferredRegister.create(Registries.STRUCTURE_TYPE,AlfheimCompanion.MOD_ID);
    public static final RegistryObject<StructureType<WorldstoneCavernStructure>> WORLDSTONE=
        REGISTRY.register("mountain_worldstone",()->()->WorldstoneCavernStructure.CODEC);
    public static final RegistryObject<StructureType<FairyReservedJigsawStructure>> FAIRY_RESERVED=
        REGISTRY.register("fairy_reserved_jigsaw",()->()->FairyReservedJigsawStructure.CODEC);
    public static final RegistryObject<StructureType<FeySkyVillageStructure>> FEY_SKY_VILLAGE=REGISTRY.register("fey_sky_village",()->()->FeySkyVillageStructure.CODEC);
    public static final RegistryObject<StructureType<HarborStructure>> HARBOR=REGISTRY.register("shoreline_harbor",()->()->HarborStructure.CODEC);
    public static final RegistryObject<StructureType<RemoteDistrictStructure>> REMOTE_DISTRICT=
        REGISTRY.register("remote_district",()->()->RemoteDistrictStructure.CODEC);
    public static final RegistryObject<StructureType<RoyalCastleStructure>> ROYAL_CASTLE=
        REGISTRY.register("royal_castle",()->()->RoyalCastleStructure.CODEC);
    public static final RegistryObject<StructureType<UpperUnderworldStructure>> UPPER_UNDERWORLD=
        REGISTRY.register("upper_underworld",()->()->UpperUnderworldStructure.CODEC);
    public static final RegistryObject<StructureType<AllocatedUndergroundStructure>> ALLOCATED_UNDERGROUND=
        REGISTRY.register("allocated_underground",()->()->AllocatedUndergroundStructure.CODEC);
    public static final RegistryObject<StructureType<VoidWarStructure>> VOID_WAR=
        REGISTRY.register("void_war",()->()->VoidWarStructure.CODEC);
    public static final RegistryObject<StructureType<VoidWarNeighborStructure>> VOID_WAR_NEIGHBOR=
        REGISTRY.register("void_war_neighbor",()->()->VoidWarNeighborStructure.CODEC);
    public static final DeferredRegister<net.minecraft.world.level.levelgen.structure.pieces.StructurePieceType> PIECES=
        DeferredRegister.create(Registries.STRUCTURE_PIECE,AlfheimCompanion.MOD_ID);
    public static final RegistryObject<net.minecraft.world.level.levelgen.structure.pieces.StructurePieceType> WORLDSTONE_PIECE=
        PIECES.register("worldstone_cavern",()->(net.minecraft.world.level.levelgen.structure.pieces.StructurePieceType.ContextlessType)WorldstoneCavernPiece::new);
    public static final RegistryObject<net.minecraft.world.level.levelgen.structure.pieces.StructurePieceType> ROYAL_FOUNDATION=
        PIECES.register("royal_foundation",()->(net.minecraft.world.level.levelgen.structure.pieces.StructurePieceType.ContextlessType)RoyalFoundationPiece::new);
    public static final RegistryObject<StructureType<MonasteryLabyrinthStructure>> MONASTERY_LABYRINTH=
        REGISTRY.register("monastery_labyrinth",()->()->MonasteryLabyrinthStructure.CODEC);
    public static final RegistryObject<net.minecraft.world.level.levelgen.structure.pieces.StructurePieceType> LABYRINTH_PIECE=
        PIECES.register("monastery_labyrinth_piece",
            ()->(net.minecraft.world.level.levelgen.structure.pieces.StructurePieceType.ContextlessType)MonasteryLabyrinthPiece::new);
    // Source-only until a rebuilt companion JAR is distributed. Never switch
    // worldgen JSON to this type before that JAR has been installed.
    public static final RegistryObject<StructureType<VoidSurfaceStructure>> VOID_SURFACE =
        REGISTRY.register("void_surface", () -> () -> VoidSurfaceStructure.CODEC);
    private ModHarborStructures() {}
}

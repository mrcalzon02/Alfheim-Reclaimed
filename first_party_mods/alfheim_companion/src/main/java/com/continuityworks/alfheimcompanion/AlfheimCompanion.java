package com.continuityworks.alfheimcompanion;

import com.continuityworks.alfheimcompanion.client.ElvenCompanionRenderer;
import com.continuityworks.alfheimcompanion.entity.ElvenCompanionEntity;
import com.continuityworks.alfheimcompanion.registry.ModEntities;
import com.continuityworks.alfheimcompanion.registry.ModItems;
import com.continuityworks.alfheimcompanion.registry.ModMenus;
import com.mojang.logging.LogUtils;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent;
import net.minecraft.client.gui.screens.MenuScreens;
import com.continuityworks.alfheimcompanion.client.CompanionInventoryScreen;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.event.entity.EntityAttributeCreationEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import net.minecraftforge.fml.event.lifecycle.FMLCommonSetupEvent;
import net.minecraftforge.event.BuildCreativeModeTabContentsEvent;
import net.minecraft.world.item.CreativeModeTabs;
import com.continuityworks.alfheimcompanion.service.CompanionChunkTickets;
import com.continuityworks.alfheimcompanion.integration.ftb.FtbIntegrationBootstrap;
import com.continuityworks.alfheimcompanion.integration.mmo.MineAndSlashIntegrationBootstrap;
import com.continuityworks.alfheimcompanion.network.CompanionNetwork;
import com.continuityworks.alfheimcompanion.brain.InferenceBootstrap;
import org.slf4j.Logger;

@Mod(AlfheimCompanion.MOD_ID)
public final class AlfheimCompanion {
    public static final String MOD_ID = "alfheim_companion";
    public static final Logger LOGGER = LogUtils.getLogger();

    public AlfheimCompanion(FMLJavaModLoadingContext context) {
        IEventBus modBus = context.getModEventBus();
        com.continuityworks.alfheimcompanion.enemy.ModThemedEnemies.initialize();
        com.continuityworks.alfheimcompanion.enemy.ModThemedEnemies.BIOME_MODIFIERS.register(modBus);
        modBus.addListener(com.continuityworks.alfheimcompanion.enemy.ModThemedEnemies::attributes);
        modBus.addListener(com.continuityworks.alfheimcompanion.enemy.ModThemedEnemies::placements);
        com.continuityworks.alfheimcompanion.monstrosity.ModMonstrosities.initialize();
        modBus.addListener(com.continuityworks.alfheimcompanion.monstrosity.ModMonstrosities::attributes);
        modBus.addListener(com.continuityworks.alfheimcompanion.monstrosity.ModMonstrosities::placements);
        com.continuityworks.alfheimcompanion.monstrosity.ModMenagerieSounds.REGISTRY.register(modBus);
        com.continuityworks.alfheimcompanion.monstrosity.MaggotMoundBlock.REGISTRY.register(modBus);
        ModEntities.REGISTRY.register(modBus);
        com.continuityworks.alfheimcompanion.fey.ModFeyHomes.BLOCKS.register(modBus);
        com.continuityworks.alfheimcompanion.fey.ModFeyHomes.ENTITIES.register(modBus);
        ModItems.REGISTRY.register(modBus);
        ModMenus.REGISTRY.register(modBus);
        com.continuityworks.alfheimcompanion.registry.ModElvenSounds.REGISTRY.register(modBus);
        com.continuityworks.alfheimcompanion.worldgen.ModHarborStructures.REGISTRY.register(modBus);
        com.continuityworks.alfheimcompanion.worldgen.ModHarborStructures.PIECES.register(modBus);
        modBus.addListener(this::registerAttributes);
        modBus.addListener(this::commonSetup);
        modBus.addListener(this::addCreativeItems);
        MinecraftForge.EVENT_BUS.register(CompanionEvents.class);
        MinecraftForge.EVENT_BUS.addListener(com.continuityworks.alfheimcompanion.fey.FeyGardenGoal::joined);
        MinecraftForge.EVENT_BUS.addListener(com.continuityworks.alfheimcompanion.worldgen.BedrockFloorGuard::onChunkLoad);
    }

    private void registerAttributes(EntityAttributeCreationEvent event) {
        event.put(ModEntities.ELVEN_CITIZEN.get(),com.continuityworks.alfheimcompanion.society.ElvenCitizenEntity.attributes().build());
        event.put(ModEntities.ELVEN_COMPANION.get(), ElvenCompanionEntity.createAttributes().build());
    }

    private void commonSetup(FMLCommonSetupEvent event) {
        event.enqueueWork(() -> {
            CompanionChunkTickets.registerValidationCallback();
            CompanionNetwork.register();
            FtbIntegrationBootstrap.registerAvailableAdapters();
            MineAndSlashIntegrationBootstrap.registerIfAvailable();
            InferenceBootstrap.installConfiguredEngine();
        });
    }

    private void addCreativeItems(BuildCreativeModeTabContentsEvent event) {
        if(event.getTabKey()==CreativeModeTabs.NATURAL_BLOCKS)event.accept(com.continuityworks.alfheimcompanion.monstrosity.MaggotMoundBlock.ITEM.get());
        if(event.getTabKey()==CreativeModeTabs.NATURAL_BLOCKS)for(var home:com.continuityworks.alfheimcompanion.fey.ModFeyHomes.ITEMS)event.accept(home.get());
        if(event.getTabKey()==CreativeModeTabs.SPAWN_EGGS)
            for(var kind:com.continuityworks.alfheimcompanion.monstrosity.MonstrosityKind.values())
                for(int variant=0;variant<3;variant++)event.accept(com.continuityworks.alfheimcompanion.monstrosity.ModMonstrosities.selection(kind,variant));
        if(event.getTabKey()==CreativeModeTabs.SPAWN_EGGS)
            for(int role=0;role<com.continuityworks.alfheimcompanion.society.ElvenSociety.IDS.length;role++)
                for(int look=0;look<4;look++)event.accept(com.continuityworks.alfheimcompanion.society.ElvenSociety.selection(role,look));
        if(event.getTabKey()==CreativeModeTabs.SPAWN_EGGS)
            com.continuityworks.alfheimcompanion.enemy.EnemySpawnItems.addCreativeItems(event);
        if (event.getTabKey() == CreativeModeTabs.TOOLS_AND_UTILITIES) {
            event.accept(ModItems.COMPANION_SIGIL);
            event.accept(ModItems.COMPANION_CLAIM_PAPER);
        }
    }

    @Mod.EventBusSubscriber(modid = MOD_ID, bus = Mod.EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
    public static final class ClientEvents {
        private ClientEvents() {}

        @net.minecraftforge.eventbus.api.SubscribeEvent
        public static void registerRenderers(EntityRenderersEvent.RegisterRenderers event) {
            event.registerEntityRenderer(ModEntities.ELVEN_CITIZEN.get(),com.continuityworks.alfheimcompanion.client.ElvenCitizenRenderer::new);
            event.registerEntityRenderer(ModEntities.ELVEN_COMPANION.get(), ElvenCompanionRenderer::new);
            com.continuityworks.alfheimcompanion.client.ThemedEnemyRenderers.register(event);
            for(var kind:com.continuityworks.alfheimcompanion.monstrosity.MonstrosityKind.values())
                event.registerEntityRenderer(com.continuityworks.alfheimcompanion.monstrosity.ModMonstrosities.TYPES.get(kind).get(),context->new com.continuityworks.alfheimcompanion.client.MonstrosityRenderer(context,kind));
        }

        @net.minecraftforge.eventbus.api.SubscribeEvent
        public static void registerEnemyLayers(EntityRenderersEvent.RegisterLayerDefinitions event) {
            for(var kind:com.continuityworks.alfheimcompanion.monstrosity.MonstrosityKind.values())
                event.registerLayerDefinition(com.continuityworks.alfheimcompanion.client.MonstrosityModel.location(kind),()->com.continuityworks.alfheimcompanion.client.MonstrosityModel.layer(kind));
            for(int role=0;role<com.continuityworks.alfheimcompanion.society.ElvenSociety.IDS.length;role++){
                final int selectedRole=role;
                event.registerLayerDefinition(com.continuityworks.alfheimcompanion.client.ElvenSocietyModels.location(role),
                    ()->com.continuityworks.alfheimcompanion.client.ElvenSocietyModels.layer(selectedRole));
                event.registerLayerDefinition(com.continuityworks.alfheimcompanion.client.ElvenSocietyModels.wardrobeLocation(role),
                    ()->com.continuityworks.alfheimcompanion.client.ElvenSocietyModels.wardrobe(selectedRole));
            }
            for(String species:com.continuityworks.alfheimcompanion.client.RegionalMonstrosityModels.SPECIES)
                event.registerLayerDefinition(com.continuityworks.alfheimcompanion.client.RegionalMonstrosityModels.location(species),
                    ()->com.continuityworks.alfheimcompanion.client.RegionalMonstrosityModels.layer(species));
            event.registerLayerDefinition(com.continuityworks.alfheimcompanion.client.MireRiftmiteModel.LAYER,
                com.continuityworks.alfheimcompanion.client.MireRiftmiteModel::layer);
            event.registerLayerDefinition(com.continuityworks.alfheimcompanion.client.SilverbarkBoneguardModel.LAYER,
                com.continuityworks.alfheimcompanion.client.SilverbarkBoneguardModel::layer);
            com.continuityworks.alfheimcompanion.client.ThemedMaterialLayer.registerLayers(event);
        }

        @net.minecraftforge.eventbus.api.SubscribeEvent
        public static void registerScreens(FMLClientSetupEvent event) {
            event.enqueueWork(() -> {
                MenuScreens.register(ModMenus.COMPANION_INVENTORY.get(), CompanionInventoryScreen::new);
                com.continuityworks.alfheimcompanion.client.EnemySpawnItemAppearance.registerProperties();
                com.continuityworks.alfheimcompanion.client.ElvenCitizenRenderer.itemProperties();
                for(var egg:com.continuityworks.alfheimcompanion.monstrosity.ModMonstrosities.EGGS.values())
                    net.minecraft.client.renderer.item.ItemProperties.register(egg.get(),new net.minecraft.resources.ResourceLocation("alfheim_companion","monstrosity_variant"),
                        (stack,world,mob,seed)->com.continuityworks.alfheimcompanion.monstrosity.ModMonstrosities.variant(stack)+1);
            });
        }
        @net.minecraftforge.eventbus.api.SubscribeEvent(priority=net.minecraftforge.eventbus.api.EventPriority.LOWEST)
        public static void registerEnemyItemColors(net.minecraftforge.client.event.RegisterColorHandlersEvent.Item event) {
            com.continuityworks.alfheimcompanion.client.EnemySpawnItemAppearance.colors(event);
        }
    }
}

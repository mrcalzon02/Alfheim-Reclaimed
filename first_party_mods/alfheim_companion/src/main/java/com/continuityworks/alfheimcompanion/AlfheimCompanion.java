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
        ModEntities.REGISTRY.register(modBus);
        ModItems.REGISTRY.register(modBus);
        ModMenus.REGISTRY.register(modBus);
        com.continuityworks.alfheimcompanion.worldgen.ModHarborStructures.REGISTRY.register(modBus);
        com.continuityworks.alfheimcompanion.worldgen.ModHarborStructures.PIECES.register(modBus);
        modBus.addListener(this::registerAttributes);
        modBus.addListener(this::commonSetup);
        modBus.addListener(this::addCreativeItems);
        MinecraftForge.EVENT_BUS.register(CompanionEvents.class);
        MinecraftForge.EVENT_BUS.addListener(com.continuityworks.alfheimcompanion.worldgen.BedrockFloorGuard::onChunkLoad);
    }

    private void registerAttributes(EntityAttributeCreationEvent event) {
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
            event.registerEntityRenderer(ModEntities.ELVEN_COMPANION.get(), ElvenCompanionRenderer::new);
            com.continuityworks.alfheimcompanion.client.ThemedEnemyRenderers.register(event);
        }

        @net.minecraftforge.eventbus.api.SubscribeEvent
        public static void registerEnemyLayers(EntityRenderersEvent.RegisterLayerDefinitions event) {
            com.continuityworks.alfheimcompanion.client.ThemedMaterialLayer.registerLayers(event);
        }

        @net.minecraftforge.eventbus.api.SubscribeEvent
        public static void registerScreens(FMLClientSetupEvent event) {
            event.enqueueWork(() -> {
                MenuScreens.register(ModMenus.COMPANION_INVENTORY.get(), CompanionInventoryScreen::new);
                com.continuityworks.alfheimcompanion.client.EnemySpawnItemAppearance.registerProperties();
            });
        }
        @net.minecraftforge.eventbus.api.SubscribeEvent(priority=net.minecraftforge.eventbus.api.EventPriority.LOWEST)
        public static void registerEnemyItemColors(net.minecraftforge.client.event.RegisterColorHandlersEvent.Item event) {
            com.continuityworks.alfheimcompanion.client.EnemySpawnItemAppearance.colors(event);
        }
    }
}

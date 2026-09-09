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
        ModEntities.REGISTRY.register(modBus);
        ModItems.REGISTRY.register(modBus);
        ModMenus.REGISTRY.register(modBus);
        modBus.addListener(this::registerAttributes);
        modBus.addListener(this::commonSetup);
        modBus.addListener(this::addCreativeItems);
        MinecraftForge.EVENT_BUS.register(CompanionEvents.class);
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
        }

        @net.minecraftforge.eventbus.api.SubscribeEvent
        public static void registerScreens(FMLClientSetupEvent event) {
            event.enqueueWork(() -> MenuScreens.register(ModMenus.COMPANION_INVENTORY.get(),
                    CompanionInventoryScreen::new));
        }
    }
}

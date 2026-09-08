package com.continuityworks.alfheimcompanion.client;

import com.continuityworks.alfheimcompanion.menu.CompanionInventoryMenu;
import com.mojang.blaze3d.systems.RenderSystem;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.player.Inventory;

public final class CompanionInventoryScreen extends AbstractContainerScreen<CompanionInventoryMenu> {
    private static final ResourceLocation TEXTURE = ResourceLocation.withDefaultNamespace(
            "textures/gui/container/generic_54.png");

    public CompanionInventoryScreen(CompanionInventoryMenu menu, Inventory inventory, Component title) {
        super(menu, inventory, title);
        imageHeight = 186;
        inventoryLabelY = imageHeight - 94;
    }

    @Override
    protected void renderBg(GuiGraphics graphics, float partialTick, int mouseX, int mouseY) {
        RenderSystem.setShaderColor(1, 1, 1, 1);
        int x = (width - imageWidth) / 2;
        int y = (height - imageHeight) / 2;
        int topHeight = 17 + 4 * 18;
        graphics.blit(TEXTURE, x, y, 0, 0, imageWidth, topHeight);
        graphics.blit(TEXTURE, x, y + topHeight, 0, 126, imageWidth, 96);
    }

    @Override
    public void render(GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {
        renderBackground(graphics);
        super.render(graphics, mouseX, mouseY, partialTick);
        renderTooltip(graphics, mouseX, mouseY);
    }
}

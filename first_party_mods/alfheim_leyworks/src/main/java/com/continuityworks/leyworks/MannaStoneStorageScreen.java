package com.continuityworks.leyworks;

import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.player.Inventory;

public final class MannaStoneStorageScreen extends AbstractContainerScreen<MannaStoneStorageMenu> {
    public MannaStoneStorageScreen(MannaStoneStorageMenu menu, Inventory inventory, Component title) {
        super(menu, inventory, title);
        imageWidth=340;
        imageHeight=222;
        inventoryLabelX=89;
        inventoryLabelY=128;
    }

    @Override protected void renderBg(GuiGraphics graphics, float partialTick, int mouseX, int mouseY) {
        int left=(width-imageWidth)/2, top=(height-imageHeight)/2;
        graphics.fill(left, top, left+imageWidth, top+imageHeight, 0xff171025);
        graphics.fill(left+3, top+3, left+imageWidth-3, top+imageHeight-3, 0xff3a2851);
        for (int i=0; i<MannaStoneStorageMenu.STORAGE_SLOTS; i++) {
            int x=left+7+(i%MannaStoneStorageMenu.COLUMNS)*18;
            int y=top+17+(i/MannaStoneStorageMenu.COLUMNS)*18;
            int color=menu.isStorageSlotActive(i) ? 0xff80629a : 0xff251d2e;
            graphics.fill(x,y,x+18,y+18,0xff120d19);
            graphics.fill(x+1,y+1,x+17,y+17,color);
        }
        for (int i=0; i<36; i++) {
            int column=i%9, row=i<27 ? i/9 : 3;
            int x=left+88+column*18;
            int y=top+(i<27 ? 139+row*18 : 197);
            graphics.fill(x,y,x+18,y+18,0xff120d19);
            graphics.fill(x+1,y+1,x+17,y+17,0xff655171);
        }
    }

    @Override protected void renderLabels(GuiGraphics graphics, int mouseX, int mouseY) {
        super.renderLabels(graphics,mouseX,mouseY);
        graphics.drawString(font, Component.translatable("container.alfheim_leyworks.storage_capacity", menu.activeSlots(), menu.chestEquivalents()),
                248, 6, 0xffe8cf73, false);
    }

    @Override public void render(GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {
        renderBackground(graphics);
        super.render(graphics,mouseX,mouseY,partialTick);
        renderTooltip(graphics,mouseX,mouseY);
    }
}

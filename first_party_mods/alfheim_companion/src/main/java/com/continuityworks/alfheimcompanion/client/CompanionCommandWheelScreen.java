package com.continuityworks.alfheimcompanion.client;

import com.continuityworks.alfheimcompanion.network.CompanionNetwork;
import com.continuityworks.alfheimcompanion.network.WheelAction;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;

public final class CompanionCommandWheelScreen extends Screen {
    private static final int RADIUS = 82;
    private WheelAction selected;

    public CompanionCommandWheelScreen() {
        super(Component.literal("Companion Commands"));
    }

    @Override
    public void render(GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {
        renderBackground(graphics);
        int cx = width / 2;
        int cy = height / 2;
        selected = selection(mouseX - cx, mouseY - cy);
        graphics.drawCenteredString(font, "Companion Commands", cx, cy - 8, 0xFFFFFFFF);
        if (selected != null) graphics.drawCenteredString(font, selected.label(), cx, cy + 7, 0xFFFFAAFF);

        WheelAction[] actions = WheelAction.values();
        for (int i = 0; i < actions.length; i++) {
            double angle = -Math.PI / 2.0 + i * Math.PI * 2.0 / actions.length;
            int x = cx + (int) Math.round(Math.cos(angle) * RADIUS);
            int y = cy + (int) Math.round(Math.sin(angle) * RADIUS);
            int color = actions[i] == selected ? 0xFFFF88FF : 0xFFE8D8FF;
            int textWidth = font.width(actions[i].label());
            graphics.fill(x - textWidth / 2 - 4, y - 4, x + textWidth / 2 + 4, y + 12,
                    actions[i] == selected ? 0xCC542B68 : 0xAA24172D);
            graphics.drawCenteredString(font, actions[i].label(), x, y, color);
        }
        super.render(graphics, mouseX, mouseY, partialTick);
    }

    @Override
    public boolean mouseReleased(double mouseX, double mouseY, int button) {
        if (button == 0 && selected != null) {
            CompanionNetwork.send(selected);
            onClose();
            return true;
        }
        return super.mouseReleased(mouseX, mouseY, button);
    }

    @Override
    public boolean isPauseScreen() { return false; }

    private WheelAction selection(double dx, double dy) {
        if (dx * dx + dy * dy < 28 * 28) return null;
        double angle = Math.atan2(dy, dx) + Math.PI / 2.0;
        if (angle < 0) angle += Math.PI * 2.0;
        int index = (int) Math.floor((angle + Math.PI / 8.0) / (Math.PI / 4.0)) % 8;
        return WheelAction.values()[index];
    }
}

package com.continuityworks.alfheimcompanion.client;

import com.continuityworks.alfheimcompanion.network.CompanionNetwork;
import com.continuityworks.alfheimcompanion.network.WheelAction;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;

public final class CompanionCommandWheelScreen extends Screen {
    private static final int RADIUS = 82;
    private static final int DEAD_ZONE = 28;
    private static final int MAX_SELECTION_RADIUS = 130;
    private static final WheelAction[] ACTIONS = WheelAction.values();
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
        graphics.drawCenteredString(font, "Release to order  |  Esc to cancel", cx, cy + 24, 0xFFD0BEDD);

        for (int i = 0; i < ACTIONS.length; i++) {
            double angle = -Math.PI / 2.0 + i * Math.PI * 2.0 / ACTIONS.length;
            int x = cx + (int) Math.round(Math.cos(angle) * RADIUS);
            int y = cy + (int) Math.round(Math.sin(angle) * RADIUS);
            int color = ACTIONS[i] == selected ? 0xFFFF88FF : 0xFFE8D8FF;
            int textWidth = font.width(ACTIONS[i].label());
            graphics.fill(x - textWidth / 2 - 4, y - 4, x + textWidth / 2 + 4, y + 12,
                    ACTIONS[i] == selected ? 0xCC542B68 : 0xAA24172D);
            graphics.drawCenteredString(font, ACTIONS[i].label(), x, y, color);
        }
        super.render(graphics, mouseX, mouseY, partialTick);
    }

    @Override
    public boolean mouseReleased(double mouseX, double mouseY, int button) {
        if (button != 0) return super.mouseReleased(mouseX, mouseY, button);

        // Recompute from the actual release position, not the last rendered hover state.
        // Releasing in the centre or beyond the wheel closes without issuing an order.
        WheelAction released = selection(mouseX - width / 2.0, mouseY - height / 2.0);
        if (released != null) CompanionNetwork.send(released);
        onClose();
        return true;
    }

    @Override
    public boolean isPauseScreen() { return false; }

    private WheelAction selection(double dx, double dy) {
        int index = WheelSelection.index(dx, dy, ACTIONS.length, DEAD_ZONE, MAX_SELECTION_RADIUS);
        return index < 0 ? null : ACTIONS[index];
    }
}

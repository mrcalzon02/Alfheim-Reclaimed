package com.continuityworks.alfheimcompanion.network;

import com.continuityworks.alfheimcompanion.service.WheelActionService;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

public record WheelActionPacket(WheelAction action) {
    public static void encode(WheelActionPacket packet, FriendlyByteBuf buffer) {
        buffer.writeByte(packet.action.ordinal());
    }

    public static WheelActionPacket decode(FriendlyByteBuf buffer) {
        int ordinal = buffer.readUnsignedByte();
        WheelAction[] values = WheelAction.values();
        return new WheelActionPacket(ordinal < values.length ? values[ordinal] : null);
    }

    public static void handle(WheelActionPacket packet, Supplier<NetworkEvent.Context> suppliedContext) {
        NetworkEvent.Context context = suppliedContext.get();
        ServerPlayer sender = context.getSender();
        if (sender != null && packet.action != null) {
            context.enqueueWork(() -> WheelActionService.execute(sender, packet.action));
        }
        context.setPacketHandled(true);
    }
}

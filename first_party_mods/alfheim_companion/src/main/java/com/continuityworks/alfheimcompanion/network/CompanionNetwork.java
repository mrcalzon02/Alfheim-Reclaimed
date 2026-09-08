package com.continuityworks.alfheimcompanion.network;

import com.continuityworks.alfheimcompanion.AlfheimCompanion;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.network.NetworkDirection;
import net.minecraftforge.network.NetworkRegistry;
import net.minecraftforge.network.simple.SimpleChannel;

import java.util.Optional;

public final class CompanionNetwork {
    private static final String VERSION = "1";
    private static final SimpleChannel CHANNEL = NetworkRegistry.ChannelBuilder
            .named(ResourceLocation.fromNamespaceAndPath(AlfheimCompanion.MOD_ID, "main"))
            .networkProtocolVersion(() -> VERSION)
            .clientAcceptedVersions(VERSION::equals)
            .serverAcceptedVersions(VERSION::equals)
            .simpleChannel();
    private static boolean registered;

    private CompanionNetwork() {}

    public static synchronized void register() {
        if (registered) return;
        CHANNEL.registerMessage(0, WheelActionPacket.class, WheelActionPacket::encode,
                WheelActionPacket::decode, WheelActionPacket::handle,
                Optional.of(NetworkDirection.PLAY_TO_SERVER));
        registered = true;
    }

    public static void send(WheelAction action) {
        CHANNEL.sendToServer(new WheelActionPacket(action));
    }
}

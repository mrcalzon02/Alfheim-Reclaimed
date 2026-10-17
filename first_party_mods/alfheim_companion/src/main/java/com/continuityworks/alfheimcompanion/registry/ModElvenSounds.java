package com.continuityworks.alfheimcompanion.registry;

import com.continuityworks.alfheimcompanion.AlfheimCompanion;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvent;
import net.minecraftforge.registries.*;

/** Shared quiet, nonverbal voices for citizens and companions. */
public final class ModElvenSounds {
    public static final DeferredRegister<SoundEvent> REGISTRY=DeferredRegister.create(ForgeRegistries.SOUND_EVENTS,AlfheimCompanion.MOD_ID);
    public static final RegistryObject<SoundEvent> MURMUR=REGISTRY.register("elf.murmur",()->SoundEvent.createVariableRangeEvent(new ResourceLocation(AlfheimCompanion.MOD_ID,"elf.murmur")));
    private ModElvenSounds(){}
}

package com.continuityworks.alfheimcompanion.monstrosity;

import com.continuityworks.alfheimcompanion.AlfheimCompanion;
import java.util.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvent;
import net.minecraftforge.registries.*;

/** Native event references are mixed and pitched in sounds.json; no missing external audio files. */
public final class ModMenagerieSounds {
    public enum Cue { AMBIENT,HURT,DEATH,STEP,WINDUP,ATTACK }
    public static final DeferredRegister<SoundEvent> REGISTRY=DeferredRegister.create(ForgeRegistries.SOUND_EVENTS,AlfheimCompanion.MOD_ID);
    private static final Map<MonstrosityKind,Map<Cue,RegistryObject<SoundEvent>>> SOUNDS=new EnumMap<>(MonstrosityKind.class);
    public static final RegistryObject<SoundEvent> MOUND=register("maggot_mound.ambient");
    private static RegistryObject<SoundEvent> register(String name){return REGISTRY.register(name,()->SoundEvent.createVariableRangeEvent(new ResourceLocation(AlfheimCompanion.MOD_ID,name)));}
    static {
        for(var kind:MonstrosityKind.values()){
            var cues=new EnumMap<Cue,RegistryObject<SoundEvent>>(Cue.class);
            for(var cue:Cue.values())cues.put(cue,register("monstrosity."+kind.id+"."+cue.name().toLowerCase(Locale.ROOT)));
            SOUNDS.put(kind,cues);
        }
    }
    public static SoundEvent get(MonstrosityKind kind,Cue cue){return SOUNDS.get(kind).get(cue).get();}
    private ModMenagerieSounds(){}
}

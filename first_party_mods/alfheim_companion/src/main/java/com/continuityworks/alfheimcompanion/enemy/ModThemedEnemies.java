package com.continuityworks.alfheimcompanion.enemy;

import com.continuityworks.alfheimcompanion.AlfheimCompanion;
import com.continuityworks.alfheimcompanion.registry.ModEntities;
import com.continuityworks.alfheimcompanion.registry.ModItems;
import com.mojang.serialization.Codec;
import java.util.List;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.monster.*;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraftforge.common.ForgeSpawnEggItem;
import net.minecraftforge.common.world.BiomeModifier;
import net.minecraftforge.event.entity.EntityAttributeCreationEvent;
import net.minecraftforge.event.entity.SpawnPlacementRegisterEvent;
import net.minecraftforge.registries.*;

/** Five entity registrations, not 390 separate AI/type registrations. */
public final class ModThemedEnemies {
    public static final RegistryObject<EntityType<ThemedZombie>> ZOMBIE=ModEntities.REGISTRY.register("biome_zombie",
        ()->EntityType.Builder.of(ThemedZombie::new,MobCategory.MONSTER).sized(0.6F,1.95F).clientTrackingRange(8).build("alfheim_companion:biome_zombie"));
    public static final RegistryObject<EntityType<ThemedSkeleton>> SKELETON=ModEntities.REGISTRY.register("biome_skeleton",
        ()->EntityType.Builder.of(ThemedSkeleton::new,MobCategory.MONSTER).sized(0.6F,1.99F).clientTrackingRange(8).build("alfheim_companion:biome_skeleton"));
    public static final RegistryObject<EntityType<ThemedPillager>> PILLAGER=ModEntities.REGISTRY.register("biome_pillager",
        ()->EntityType.Builder.of(ThemedPillager::new,MobCategory.MONSTER).sized(0.6F,1.95F).clientTrackingRange(8).build("alfheim_companion:biome_pillager"));
    public static final RegistryObject<EntityType<ThemedEnderman>> ENDERMAN=ModEntities.REGISTRY.register("biome_enderman",
        ()->EntityType.Builder.of(ThemedEnderman::new,MobCategory.MONSTER).sized(0.6F,2.9F).clientTrackingRange(8).build("alfheim_companion:biome_enderman"));
    public static final RegistryObject<EntityType<ThemedEndermite>> ENDERMITE=ModEntities.REGISTRY.register("biome_endermite",
        ()->EntityType.Builder.of(ThemedEndermite::new,MobCategory.MONSTER).sized(0.4F,0.3F).clientTrackingRange(8).build("alfheim_companion:biome_endermite"));
    public static final List<RegistryObject<Item>> EGGS=List.of(
        egg("zombie",ZOMBIE,0x6D8064,0xC2AD7A),egg("skeleton",SKELETON,0xADA990,0x759783),
        egg("pillager",PILLAGER,0x7A8186,0xB18FBD),egg("enderman",ENDERMAN,0x39364D,0xAC94CD),
        egg("endermite",ENDERMITE,0x6C587F,0xB3C5B3));
    public static final DeferredRegister<Codec<? extends BiomeModifier>> BIOME_MODIFIERS=
        DeferredRegister.create(ForgeRegistries.Keys.BIOME_MODIFIER_SERIALIZERS,AlfheimCompanion.MOD_ID);
    public static final RegistryObject<Codec<? extends BiomeModifier>> MODIFIER=
        BIOME_MODIFIERS.register("themed_enemies",()->ThemedEnemyBiomeModifier.CODEC);
    private static RegistryObject<Item> egg(String id,RegistryObject<? extends EntityType<? extends Mob>> type,int base,int accent) {
        String label=switch(id) {
            case "zombie"->"Revenant";case "skeleton"->"Boneguard";case "pillager"->"Outcast";
            case "enderman"->"Riftwalker";default->"Riftmite";
        };
        return ModItems.REGISTRY.register("biome_"+id+"_spawn_egg",()->new ThemedSpawnEggItem(type,base,accent,label));
    }
    public static void initialize() {} // force registration before the buses are attached
    public static void attributes(EntityAttributeCreationEvent event) {
        event.put(ZOMBIE.get(),Zombie.createAttributes().build());
        event.put(SKELETON.get(),AbstractSkeleton.createAttributes().build());
        event.put(PILLAGER.get(),Pillager.createAttributes().build());
        event.put(ENDERMAN.get(),EnderMan.createAttributes().build());
        event.put(ENDERMITE.get(),Endermite.createAttributes().build());
    }
    private static <T extends Monster> void placement(SpawnPlacementRegisterEvent event,EntityType<T> type) {
        event.register(type,SpawnPlacements.Type.ON_GROUND,Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
            (t,level,reason,pos,random)-> {
                var id=level.getLevel().dimension().location().toString();
                return (id.equals("minecraft:overworld") || id.equals("mythicbotany:alfheim"))
                    && Monster.checkMonsterSpawnRules(t,level,reason,pos,random);
            },SpawnPlacementRegisterEvent.Operation.REPLACE);
    }
    public static void placements(SpawnPlacementRegisterEvent event) {
        placement(event,ZOMBIE.get());placement(event,SKELETON.get());placement(event,PILLAGER.get());
        placement(event,ENDERMAN.get());placement(event,ENDERMITE.get());
    }
    private ModThemedEnemies() {}
}

package com.continuityworks.alfheimcompanion.monstrosity;

import com.continuityworks.alfheimcompanion.registry.*;
import java.util.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.item.*;
import net.minecraft.network.chat.Component;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraftforge.common.ForgeSpawnEggItem;
import net.minecraftforge.event.entity.*;
import net.minecraftforge.registries.RegistryObject;

public final class ModMonstrosities {
    public static final Map<MonstrosityKind,RegistryObject<EntityType<MonstrosityEntity>>> TYPES=new EnumMap<>(MonstrosityKind.class);
    public static final Map<MonstrosityKind,RegistryObject<Item>> EGGS=new EnumMap<>(MonstrosityKind.class);
    static {
        for(var kind:MonstrosityKind.values()){
            var type=ModEntities.REGISTRY.register(kind.id,()->EntityType.Builder.<MonstrosityEntity>of((t,l)->new MonstrosityEntity(t,l,kind),MobCategory.MONSTER)
                .sized(kind.width,kind.height).clientTrackingRange(10).build("alfheim_companion:"+kind.id));TYPES.put(kind,type);
            EGGS.put(kind,ModItems.REGISTRY.register(kind.id+"_spawn_egg",()->new ForgeSpawnEggItem(type,0x57654A,0xC9B481,new Item.Properties()){
                @Override public Component getName(ItemStack stack){return Component.literal(kind.variants[variant(stack)]+" "+kind.label+" Spawn Egg");}
            }));
        }
    }
    public static void initialize(){}
    public static int variant(ItemStack stack){var nbt=stack.getTagElement("EntityTag");return nbt==null?0:Math.floorMod(nbt.getInt("MonstrosityVariant"),3);}
    public static ItemStack selection(MonstrosityKind kind,int variant){var stack=new ItemStack(EGGS.get(kind).get());stack.getOrCreateTagElement("EntityTag").putInt("MonstrosityVariant",Math.floorMod(variant,3));return stack;}
    public static void attributes(EntityAttributeCreationEvent event){for(var kind:MonstrosityKind.values())event.put(TYPES.get(kind).get(),MonstrosityEntity.attributes(kind).build());}
    public static void placements(SpawnPlacementRegisterEvent event){
        for(var kind:MonstrosityKind.values())event.register(TYPES.get(kind).get(),SpawnPlacements.Type.ON_GROUND,Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
            (type,level,reason,pos,random)->level.getLevel().dimension().location().toString().equals("mythicbotany:alfheim")
                &&Monster.checkMonsterSpawnRules(type,level,reason,pos,random)
                &&level.noCollision(type.getAABB(pos.getX()+.5,pos.getY(),pos.getZ()+.5)),SpawnPlacementRegisterEvent.Operation.REPLACE);
    }
    private ModMonstrosities(){}
}

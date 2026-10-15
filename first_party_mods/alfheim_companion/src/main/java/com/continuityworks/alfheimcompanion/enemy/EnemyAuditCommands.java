package com.continuityworks.alfheimcompanion.enemy;

import com.continuityworks.alfheimcompanion.AlfheimCompanion;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import java.util.List;
import net.minecraft.commands.Commands;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.network.chat.Component;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.monster.Monster;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

/** Permissioned evidence: base audit is read-only; explicit probe creates five test mobs. */
@Mod.EventBusSubscriber(modid=AlfheimCompanion.MOD_ID)
public final class EnemyAuditCommands {
    @SubscribeEvent public static void register(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("alfheim_enemies_audit").requires(s->s.hasPermission(2)).executes(c->{
            var source=c.getSource();var level=source.getLevel();var registry=level.registryAccess().registryOrThrow(Registries.BIOME);
            List<EntityType<? extends Monster>> types=List.of(ModThemedEnemies.ZOMBIE.get(),ModThemedEnemies.SKELETON.get(),
                ModThemedEnemies.PILLAGER.get(),ModThemedEnemies.ENDERMAN.get(),ModThemedEnemies.ENDERMITE.get());
            JsonObject report=new JsonObject();report.addProperty("dimension",level.dimension().location().toString());
            JsonArray biomes=new JsonArray();int gaps=0,vanilla=0;
            var ids=new java.util.ArrayList<String>();for(var profile:EnemyProfiles.ALL) ids.add(profile.biome());
            ids.addAll(List.of("minecraft:plains","minecraft:desert","minecraft:taiga","minecraft:mushroom_fields"));
            for(String id:ids) {
                var biome=registry.getHolderOrThrow(ResourceKey.create(Registries.BIOME,new ResourceLocation(id)));
                var entries=biome.value().getMobSettings().getMobs(MobCategory.MONSTER).unwrap();
                JsonObject row=new JsonObject();row.addProperty("biome",id);JsonArray mobs=new JsonArray();
                for(var type:types) {
                    int weight=0,entriesForType=0;
                    for(var data:entries) if(data.type==type) {weight+=data.getWeight().asInt();entriesForType++;}
                    if(weight==0) gaps++;
                    JsonObject mob=new JsonObject();mob.addProperty("type",ForgeRegistries.ENTITY_TYPES.getKey(type).toString());
                    mob.addProperty("weight",weight);mob.addProperty("entries",entriesForType);mobs.add(mob);
                }
                for(var data:entries) if(List.of(EntityType.ZOMBIE,EntityType.SKELETON,EntityType.PILLAGER,EntityType.ENDERMAN,EntityType.ENDERMITE).contains(data.type)) vanilla++;
                row.add("mobs",mobs);biomes.add(row);
            }
            report.add("biomes",biomes);report.addProperty("coverage_gaps",gaps);report.addProperty("unreplaced_vanilla_entries",vanilla);
            JsonArray rules=new JsonArray();var pos=net.minecraft.core.BlockPos.containing(source.getPosition());
            for(var type:types) {
                int accepted=0;
                for(int attempt=0;attempt<32;attempt++)
                    if(SpawnPlacements.checkSpawnRules(type,level,MobSpawnType.NATURAL,pos,RandomSource.create(700+attempt))) accepted++;
                JsonObject row=new JsonObject();row.addProperty("type",ForgeRegistries.ENTITY_TYPES.getKey(type).toString());
                row.addProperty("natural_rule_acceptances",accepted);rules.add(row);
            }
            report.add("rules_at_command_position",rules);
            source.sendSuccess(()->Component.literal("ALFHEIM_ENEMY_AUDIT "+report),false);
            return gaps==0 && vanilla==0 ? 1 : 0;
        }).then(Commands.literal("probe").executes(c->probe(c.getSource()))));
    }
    private static int probe(net.minecraft.commands.CommandSourceStack source) {
        var level=source.getLevel();String dimension=level.dimension().location().toString();
        if(!dimension.equals("mythicbotany:alfheim") && !dimension.equals("minecraft:overworld")) return 0;
        List<EntityType<? extends Monster>> types=List.of(ModThemedEnemies.ZOMBIE.get(),ModThemedEnemies.SKELETON.get(),
            ModThemedEnemies.PILLAGER.get(),ModThemedEnemies.ENDERMAN.get(),ModThemedEnemies.ENDERMITE.get());
        JsonObject report=new JsonObject();report.addProperty("dimension",dimension);JsonArray mobs=new JsonArray();
        var origin=net.minecraft.core.BlockPos.containing(source.getPosition());
        for(int i=0;i<types.size();i++) {
            var pos=origin.offset(i*3,0,0);var mob=types.get(i).spawn(level,pos,MobSpawnType.NATURAL);
            if(mob==null) throw new IllegalStateException("Enemy spawn factory rejected "+types.get(i));
            // The factory has run vanilla equipment and our appearance initialization.
            mob.setNoAi(true);mob.setPersistenceRequired();mob.setInvulnerable(true);
            mob.addTag("alfheim_enemy_finalize_probe");
            JsonObject row=new JsonObject();row.addProperty("type",ForgeRegistries.ENTITY_TYPES.getKey(mob.getType()).toString());
            row.addProperty("biome",EnemyProfiles.get(EnemyAppearance.profile(mob)).biome());
            row.addProperty("expected_biome",EnemyProfiles.get(EnemyProfiles.choose(level.getBiome(pos))).biome());
            row.addProperty("style",EnemyAppearance.style(mob));row.addProperty("loot",mob.getLootTable().toString());
            row.addProperty("main_hand",ForgeRegistries.ITEMS.getKey(mob.getMainHandItem().getItem()).toString());mobs.add(row);
        }
        report.add("mobs",mobs);source.sendSuccess(()->Component.literal("ALFHEIM_ENEMY_FACTORY "+report),false);return mobs.size();
    }
    private EnemyAuditCommands() {}
}

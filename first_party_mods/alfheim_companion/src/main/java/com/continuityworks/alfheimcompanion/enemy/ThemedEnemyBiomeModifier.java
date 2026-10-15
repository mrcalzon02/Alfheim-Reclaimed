package com.continuityworks.alfheimcompanion.enemy;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.Holder;
import net.minecraft.core.HolderSet;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.biome.MobSpawnSettings.SpawnerData;
import net.minecraftforge.common.world.BiomeModifier;
import net.minecraftforge.common.world.ModifiableBiomeInfo;

/** Replace existing entries in place, preserving weight, group size and spawn cost.
 * Missing species receive small defaults. No spawn cap or terrain setting changes.
 */
public record ThemedEnemyBiomeModifier(HolderSet<Biome> biomes) implements BiomeModifier {
    public static final Codec<ThemedEnemyBiomeModifier> CODEC=RecordCodecBuilder.create(i->i.group(
        Biome.LIST_CODEC.fieldOf("biomes").forGetter(ThemedEnemyBiomeModifier::biomes)
    ).apply(i,ThemedEnemyBiomeModifier::new));
    @Override public void modify(Holder<Biome> biome,Phase phase,ModifiableBiomeInfo.BiomeInfo.Builder builder) {
        if(phase!=Phase.AFTER_EVERYTHING || !biomes.contains(biome)) return;
        var settings=builder.getMobSpawnSettings();
        var entries=settings.getSpawner(MobCategory.MONSTER);
        List<EntityType<?>> originals=List.of(EntityType.ZOMBIE,EntityType.SKELETON,EntityType.PILLAGER,EntityType.ENDERMAN,EntityType.ENDERMITE);
        List<EntityType<?>> replacements=List.of(ModThemedEnemies.ZOMBIE.get(),ModThemedEnemies.SKELETON.get(),
            ModThemedEnemies.PILLAGER.get(),ModThemedEnemies.ENDERMAN.get(),ModThemedEnemies.ENDERMITE.get());
        int[] defaults={20,20,2,4,2};
        for(int species=0;species<originals.size();species++) {
            EntityType<?> original=originals.get(species), replacement=replacements.get(species);
            boolean found=entries.stream().anyMatch(e->e.type==replacement);
            for(SpawnerData entry:new ArrayList<>(entries)) {
                if(entry.type!=original) continue;
                entries.remove(entry);
                entries.add(new SpawnerData(replacement,entry.getWeight().asInt(),entry.minCount,entry.maxCount));
                found=true;
            }
            if(!found) entries.add(new SpawnerData(replacement,defaults[species],1,species==0 || species==1 ? 3 : 1));
            var cost=settings.getCost(original);
            if(cost!=null) settings.addMobCharge(replacement,cost.charge(),cost.energyBudget());
        }
    }
    @Override public Codec<? extends BiomeModifier> codec() { return CODEC; }
}

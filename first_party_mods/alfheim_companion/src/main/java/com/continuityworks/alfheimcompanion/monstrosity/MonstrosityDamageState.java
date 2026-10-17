package com.continuityworks.alfheimcompanion.monstrosity;

import net.minecraft.world.entity.LivingEntity;
import net.minecraftforge.fml.ModList;

/** Observe replaced damage; never issue a second hit when another mod owns its calculation. */
public record MonstrosityDamageState(float health,float absorption,float magicShield) {
    public static MonstrosityDamageState capture(LivingEntity target){
        return new MonstrosityDamageState(target.getHealth(),target.getAbsorptionAmount(),shield(target));
    }
    public boolean wasHarmed(LivingEntity target){
        return target.getHealth()<health||target.getAbsorptionAmount()<absorption||shield(target)<magicShield;
    }
    private static float shield(LivingEntity target){return ModList.get().isLoaded("mmorpg")?MnsAccess.shield(target):0;}
    private static final class MnsAccess {
        static float shield(LivingEntity target){return com.robertx22.mine_and_slash.capability.entity.EntityData.get(target).getResources().getMagicShield();}
    }
}

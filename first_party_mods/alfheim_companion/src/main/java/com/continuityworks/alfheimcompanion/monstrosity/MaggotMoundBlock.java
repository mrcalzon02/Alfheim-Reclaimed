package com.continuityworks.alfheimcompanion.monstrosity;

import com.continuityworks.alfheimcompanion.AlfheimCompanion;
import com.continuityworks.alfheimcompanion.registry.ModItems;
import net.minecraft.core.BlockPos;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.item.*;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.*;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.phys.shapes.*;
import net.minecraftforge.registries.*;

/** Decorative fleshy nest cover; real bounded vanilla spawners live in the corpse burrows. */
public final class MaggotMoundBlock extends Block {
    public static final IntegerProperty DECAY=IntegerProperty.create("decay",0,2);
    public static final DeferredRegister<Block> REGISTRY=DeferredRegister.create(ForgeRegistries.BLOCKS,AlfheimCompanion.MOD_ID);
    public static final RegistryObject<Block> MOUND=REGISTRY.register("maggot_mound",MaggotMoundBlock::new);
    public static final RegistryObject<Item> ITEM=ModItems.REGISTRY.register("maggot_mound",()->new BlockItem(MOUND.get(),new Item.Properties()));
    public MaggotMoundBlock(){super(Properties.of().mapColor(net.minecraft.world.level.material.MapColor.DIRT).strength(.7F,1.5F).sound(SoundType.SLIME_BLOCK).noOcclusion());registerDefaultState(stateDefinition.any().setValue(DECAY,0));}
    @Override protected void createBlockStateDefinition(StateDefinition.Builder<Block,BlockState> builder){builder.add(DECAY);}
    @Override public VoxelShape getShape(BlockState state,BlockGetter level,BlockPos pos,CollisionContext context){return Block.box(0,0,0,16,11,16);}
    @Override public void animateTick(BlockState state,Level level,BlockPos pos,RandomSource random){
        if(random.nextInt(100)==0)level.playLocalSound(pos.getX()+.5,pos.getY()+.5,pos.getZ()+.5,ModMenagerieSounds.MOUND.get(),SoundSource.BLOCKS,.15F,.85F+random.nextFloat()*.2F,false);
    }
}

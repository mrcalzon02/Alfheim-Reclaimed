package com.continuityworks.alfheimcompanion.worldgen;

import com.continuityworks.alfheimcompanion.AlfheimCompanion;
import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;
import net.minecraft.core.BlockPos;
import net.minecraft.tags.FluidTags;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.HashMap;

@Mod.EventBusSubscriber(modid=AlfheimCompanion.MOD_ID)
public final class HarborCommands {
    @SubscribeEvent public static void register(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("alfheimharbor").requires(s->s.hasPermission(2))
            .then(Commands.literal("audit_generated").then(Commands.argument("x",IntegerArgumentType.integer()).then(Commands.argument("z",IntegerArgumentType.integer()).executes(c->generated(c)))))
            .then(Commands.literal("audit_bounded").then(Commands.argument("x",IntegerArgumentType.integer()).then(Commands.argument("z",IntegerArgumentType.integer()).executes(c->generated(c,HarborGeometry.PARTS,null,true)))))
            .then(Commands.literal("audit_proposal").then(Commands.argument("proposal",StringArgumentType.word()).then(Commands.argument("x",IntegerArgumentType.integer()).then(Commands.argument("z",IntegerArgumentType.integer()).executes(c->proposal(c))))))
            .then(Commands.literal("audit").then(Commands.argument("x",IntegerArgumentType.integer()).then(Commands.argument("z",IntegerArgumentType.integer()).executes(c->run(c,false)))))
            .then(Commands.literal("place_checked").then(Commands.argument("x",IntegerArgumentType.integer()).then(Commands.argument("z",IntegerArgumentType.integer()).executes(c->run(c,true))))));
    }
    private static int generated(com.mojang.brigadier.context.CommandContext<net.minecraft.commands.CommandSourceStack> c) {
        return generated(c,HarborGeometry.PARTS,null);
    }
    private static int proposal(com.mojang.brigadier.context.CommandContext<net.minecraft.commands.CommandSourceStack> c) {
        String name=StringArgumentType.getString(c,"proposal");
        var parts=HarborFootprintProposals.get(name);
        if(parts==null) {c.getSource().sendFailure(Component.literal("Unknown harbor footprint proposal"));return 0;}
        return generated(c,parts,name);
    }
    private static int generated(com.mojang.brigadier.context.CommandContext<net.minecraft.commands.CommandSourceStack> c,HarborGeometry.Part[] parts,String proposal) {
        return generated(c,parts,proposal,false);
    }
    private static int generated(com.mojang.brigadier.context.CommandContext<net.minecraft.commands.CommandSourceStack> c,HarborGeometry.Part[] parts,String proposal,boolean bounded) {
        var level=c.getSource().getLevel();int x=IntegerArgumentType.getInteger(c,"x"),z=IntegerArgumentType.getInteger(c,"z");
        if(!level.dimension().location().toString().equals("mythicbotany:alfheim")) {
            c.getSource().sendFailure(Component.literal("Harbor rejected: wrong dimension"));return 0;
        }
        var biome=level.getChunkSource().getGenerator().getBiomeSource().getNoiseBiome(x>>2,(level.getSeaLevel()+2)>>2,z>>2,level.getChunkSource().randomState().sampler());
        boolean eligible=biome.is(net.minecraft.tags.TagKey.create(net.minecraft.core.registries.Registries.BIOME,new net.minecraft.resources.ResourceLocation("alfheim","has_harbor_complex")));
        String biomeName=biome.unwrapKey().map(k->k.location().toString()).orElse("unknown");
        long start=System.nanoTime();
        var result=bounded?HarborStructure.auditGeneratedBounded(level.getChunkSource().getGenerator(),level.getChunkSource().randomState(),level,x,z,true,parts)
            :HarborStructure.auditGenerated(level.getChunkSource().getGenerator(),level.getChunkSource().randomState(),level,x,z,true,parts);
        long ms=(System.nanoTime()-start)/1000000;
        String prefix=bounded?"Harbor bounded audit":proposal==null?"Harbor generated audit":"Harbor proposal audit proposal="+proposal;
        c.getSource().sendSuccess(()->Component.literal(prefix+" x="+x+" z="+z+" accepted="+result.site().isPresent()+" columns="+result.columns()+" parity="+result.parity()+" ms="+ms+" eligible="+eligible+" biome="+biomeName+" rotation="+result.site().map(v->v.rotation()).orElse(-1)+" lift="+result.site().map(v->v.quayLift()).orElse(-1)+" profile="+result.profile()+" attempts="+result.attempts()),false);
        return result.site().isPresent()?1:0;
    }

    private static int run(com.mojang.brigadier.context.CommandContext<net.minecraft.commands.CommandSourceStack> c,boolean place) {
        var level=c.getSource().getLevel();
        if(!level.dimension().location().toString().equals("mythicbotany:alfheim")) {
            c.getSource().sendFailure(Component.literal("Harbor rejected: wrong dimension"));return 0;
        }
        int sea=level.getChunkSource().getGenerator().getSeaLevel();
        var cache=new HashMap<Long,HarborSite.Column>();
        var site=HarborSite.find(IntegerArgumentType.getInteger(c,"x"),IntegerArgumentType.getInteger(c,"z"),sea,(x,z)->cache.computeIfAbsent(BlockPos.asLong(x,0,z),key->{
            if(!level.hasChunk(x>>4,z>>4)) return null;
            return new HarborSite.Column(level.getHeight(Heightmap.Types.WORLD_SURFACE,x,z),level.getHeight(Heightmap.Types.OCEAN_FLOOR,x,z),level.getFluidState(new BlockPos(x,sea-1,z)).is(FluidTags.WATER));
        }));
        if(site.isEmpty()) {c.getSource().sendSuccess(()->Component.literal("Harbor rejected: waterline, relief, support or loaded footprint"),false);return 0;}
        var s=site.get();
        if(place) HarborStructure.pieces(level.getStructureManager(),s,piece->piece.place(level,level.structureManager(),level.getChunkSource().getGenerator(),level.random,piece.getBoundingBox(),new BlockPos(s.x(),s.baseY(),s.z()),false));
        c.getSource().sendSuccess(()->Component.literal("Harbor "+(place?"placed":"accepted")+": rotation="+s.rotation()+" quay="+(s.baseY()+8)),false);
        return 1;
    }
}

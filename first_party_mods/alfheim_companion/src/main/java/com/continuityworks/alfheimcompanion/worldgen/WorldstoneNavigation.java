package com.continuityworks.alfheimcompanion.worldgen;

import com.continuityworks.alfheimcompanion.AlfheimCompanion;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.NbtUtils;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.*;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureCheckResult;
import net.minecraft.world.level.levelgen.structure.placement.RandomSpreadStructurePlacement;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.server.ServerLifecycleHooks;
import java.util.*;

/** Finite, tick-budgeted natural-site search; never generates or force-loads chunks. */
@Mod.EventBusSubscriber(modid=AlfheimCompanion.MOD_ID)
public final class WorldstoneNavigation {
    private static final Map<UUID,Task> TASKS=new HashMap<>();
    public static final class Task {
        public final ItemStack stack;
        private final ServerLevel level;
        private final WorldstoneCavernStructure structure;
        private final List<ChunkPos> candidates=new ArrayList<>();
        private int index;
        public boolean complete;
        public BlockPos target;
        public Task(ServerLevel level,BlockPos origin,ItemStack stack) {
            this.level=level;this.stack=stack;
            structure=(WorldstoneCavernStructure)level.registryAccess().registryOrThrow(Registries.STRUCTURE).get(WorldstoneCavernStructure.ID);
            var set=level.registryAccess().registryOrThrow(Registries.STRUCTURE_SET).get(WorldstoneCavernStructure.ID);
            if(structure==null || set==null || !(set.placement() instanceof RandomSpreadStructurePlacement placement)){complete=true;return;}
            int rx=Math.floorDiv(origin.getX()>>4,placement.spacing()),rz=Math.floorDiv(origin.getZ()>>4,placement.spacing());
            for(int dx=-32;dx<=32;dx++)for(int dz=-32;dz<=32;dz++)
                candidates.add(placement.getPotentialStructureChunk(level.getSeed(),(rx+dx)*placement.spacing(),(rz+dz)*placement.spacing()));
            candidates.sort(Comparator.<ChunkPos>comparingDouble(p->distance(p,origin)).thenComparingLong(ChunkPos::toLong));
        }
        private static double distance(ChunkPos p,BlockPos origin) {
            double dx=(double)p.getMiddleBlockX()-origin.getX(),dz=(double)p.getMiddleBlockZ()-origin.getZ();return dx*dx+dz*dz;
        }
        public int tested(){return index;}
        public void step(int limit) {
            if(complete)return;
            var generator=level.getChunkSource().getGenerator();long begin=System.nanoTime();
            for(int i=0;i<limit && index<candidates.size();i++) {
                if(i>0 && System.nanoTime()-begin>3_000_000L)break;
                var p=candidates.get(index++);
                var context=new Structure.GenerationContext(level.registryAccess(),generator,generator.getBiomeSource(),
                    level.getChunkSource().randomState(),level.getStructureManager(),level.getSeed(),p,level,structure.biomes()::contains);
                if(!structure.rejection(context).equals("none"))continue;
                // Old chunks that predate this feature must not become false destinations.
                if(level.structureManager().checkStructurePresence(p,structure,false)==StructureCheckResult.START_NOT_PRESENT)continue;
                if(structure.findValidGenerationPoint(context).isEmpty())continue;
                target=new BlockPos(p.getMiddleBlockX(),60,p.getMiddleBlockZ());complete=true;
                var tag=stack.getOrCreateTag();tag.put("LodestonePos",NbtUtils.writeBlockPos(target));
                tag.putString("LodestoneDimension","mythicbotany:alfheim");tag.putBoolean("LodestoneTracked",false);
                tag.putBoolean("WorldstoneSeeking",false);return;
            }
            if(index>=candidates.size()){complete=true;stack.getOrCreateTag().putBoolean("WorldstoneSeeking",false);}
        }
    }
    public static void begin(ServerPlayer player,ItemStack stack) {
        var current=TASKS.get(player.getUUID());
        if(current!=null && current.stack==stack)return;
        if(current!=null)current.stack.getOrCreateTag().putBoolean("WorldstoneSeeking",false);
        stack.getOrCreateTag().putBoolean("WorldstoneSeeking",true);
        TASKS.put(player.getUUID(),new Task(player.serverLevel(),player.blockPosition(),stack));
        player.displayClientMessage(Component.literal("Listening for the Worldstone..."),true);
    }
    public static boolean isSeeking(UUID player,ItemStack stack) {
        var task=TASKS.get(player);return task!=null && task.stack==stack && !task.complete;
    }
    @SubscribeEvent public static void tick(TickEvent.ServerTickEvent event) {
        if(event.phase!=TickEvent.Phase.END)return;
        var server=ServerLifecycleHooks.getCurrentServer();if(server==null)return;
        var iterator=TASKS.entrySet().iterator();
        while(iterator.hasNext()) {
            var entry=iterator.next();var task=entry.getValue();var player=server.getPlayerList().getPlayer(entry.getKey());
            if(player==null || player.serverLevel()!=task.level || java.util.stream.Stream.concat(player.getInventory().items.stream(),player.getInventory().offhand.stream()).noneMatch(s->s==task.stack)) {
                task.stack.getOrCreateTag().putBoolean("WorldstoneSeeking",false);iterator.remove();continue;
            }
            task.step(4);
            if(!task.complete)continue;
            String text=task.target==null?"No Worldstone answers from here. Try again in another region.":
                "The Worldstone calls from "+task.target.getX()+", "+task.target.getZ()+".";
            player.displayClientMessage(Component.literal(text),false);iterator.remove();
        }
    }
    @SubscribeEvent public static void stopped(ServerStoppedEvent event){TASKS.clear();}
    private WorldstoneNavigation(){}
}

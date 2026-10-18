package com.continuityworks.alfheimcompanion.worldgen;

import com.continuityworks.alfheimcompanion.AlfheimCompanion;
import com.google.gson.Gson;
import com.google.gson.JsonElement;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.server.packs.resources.SimpleJsonResourceReloadListener;
import net.minecraft.util.profiling.ProfilerFiller;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.PoolElementStructurePiece;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructurePiece;
import net.minecraftforge.event.AddReloadListenerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Data-driven ground contact; never changes another mod's structure or existing chunks. */
@Mod.EventBusSubscriber(modid=AlfheimCompanion.MOD_ID)
public final class TerrainAffordances extends SimpleJsonResourceReloadListener {
    public record Profile(String mode,int ground,int edge,int feather,int depth,int rise,boolean water,String material) {
        public Profile {
            if(edge<0||edge>4||feather<0||feather>4||depth<0||depth>96||ground<0||ground>48||rise<0||rise>16)
                throw new IllegalArgumentException("Invalid terrain affordance bounds");
            if(mode.equals("grounded")&&(edge<1||depth<1))
                throw new IllegalArgumentException("Grounded structures require an edge and bounded support");
        }
        public int halo(){return edge+feather;}
        public boolean fits(int top,int surface,int sea) {
            return surface> -64 && top-(surface-1)<=depth && (surface-1)-top<=rise
                && (water||surface>sea);
        }
    }
    private static volatile Map<ResourceLocation,Profile> profiles=Map.of();
    private static volatile java.util.Set<ResourceLocation> activeGroundPlates=java.util.Set.of();
    private TerrainAffordances(){super(new Gson(),"terrain_affordances");}
    @SubscribeEvent public static void register(AddReloadListenerEvent event){event.addListener(new TerrainAffordances());}
    @Override protected void apply(Map<ResourceLocation,JsonElement> files,ResourceManager resources,ProfilerFiller profiler){
        var next=new HashMap<ResourceLocation,Profile>();
        var active=new java.util.HashSet<ResourceLocation>();
        files.forEach((id,element)->{
            var j=element.getAsJsonObject();
            if(j.has("activate_ground_adapter")&&j.get("activate_ground_adapter").getAsBoolean())active.add(id);
            next.put(id,new Profile(j.get("mode").getAsString(),j.get("ground_offset").getAsInt(),
                j.get("edge_width").getAsInt(),j.get("feather_width").getAsInt(),j.get("max_support_depth").getAsInt(),
                j.get("max_terrain_rise").getAsInt(),j.get("allow_water").getAsBoolean(),j.get("foundation_material").getAsString()));
        });
        profiles=Map.copyOf(next);
        activeGroundPlates=java.util.Set.copyOf(active);
        AlfheimCompanion.LOGGER.info("Loaded {} structure terrain-affordance contracts",profiles.size());
    }
    public static Map<ResourceLocation,Profile> profiles(){return profiles;}
    public static Optional<Structure.GenerationStub> fit(Structure owner,Structure.GenerationContext c,
            Optional<Structure.GenerationStub> proposed){
        if(proposed.isEmpty())return proposed;
        var id=c.registryAccess().registryOrThrow(Registries.STRUCTURE).getKey(owner);
        var profile=profiles.get(id);
        if(profile==null)throw new IllegalStateException("Missing terrain-affordance contract for "+id);
        if(!profile.mode().equals("grounded"))return proposed;
        // New foundation geometry requires saved-world acceptance. Until its
        // explicit per-family activation, retain the existing working layout.
        if(!activeGroundPlates.contains(id))return proposed;
        var stub=proposed.get();
        var originals=stub.getPiecesBuilder().build().pieces();
        var plates=new ArrayList<StructurePiece>();
        // One noise lattice per member. A hard budget prevents unbounded terrain searches.
        var heights=new HashMap<Long,Integer>();
        for(var original:originals){
            if(!(original instanceof PoolElementStructurePiece p))continue;
            var b=p.getBoundingBox();int top=p.getPosition().getY()+profile.ground()-1;
            // A surface headworks also owns a descending stair chain. Only its
            // surface member gets an apron; basement/shaft pieces keep their host.
            if(id.getPath().equals("deepworks_headworks")&&top<stub.position().getY()-8)continue;
            if(top-profile.depth()<=c.heightAccessor().getMinBuildHeight()||top+1>=c.heightAccessor().getMaxBuildHeight())return Optional.empty();
            for(int x:new int[]{b.minX()-profile.halo(),(b.minX()+b.maxX())/2,b.maxX()+profile.halo()})
                for(int z:new int[]{b.minZ()-profile.halo(),(b.minZ()+b.maxZ())/2,b.maxZ()+profile.halo()}){
                    long key=((long)x<<32)^(z&0xffffffffL);
                    Integer height=heights.get(key);
                    if(height==null){
                        if(heights.size()>=256)return Optional.empty();
                        height=c.chunkGenerator().getBaseHeight(x,z,Heightmap.Types.OCEAN_FLOOR_WG,c.heightAccessor(),c.randomState());
                        heights.put(key,height);
                    }
                    if(!profile.fits(top,height,c.chunkGenerator().getSeaLevel()))return Optional.empty();
                }
            plates.add(new GroundPlatePiece(b.minX(),b.minZ(),b.maxX(),b.maxZ(),top,profile));
        }
        return Optional.of(new Structure.GenerationStub(stub.position(),builder->{
            plates.forEach(builder::addPiece);
            originals.forEach(builder::addPiece);
        }));
    }
}

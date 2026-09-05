package alfheim.voidmargin.mixin;

import alfheim.voidmargin.RegionalAquifer;
import net.minecraft.world.level.levelgen.*;
import net.minecraft.world.level.levelgen.blending.Blender;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(value=NoiseChunk.class, remap=false)
public abstract class NoiseChunkMixin {
    @Shadow @Final @Mutable private Aquifer f_188728_;

    @Inject(method="<init>",at=@At("RETURN"),require=1,remap=false)
    private void alfheim$regionalAquifer(int cells, RandomState state, int x, int z,
            NoiseSettings noise, DensityFunctions.BeardifierOrMarker beard,
            NoiseGeneratorSettings settings, Aquifer.FluidPicker picker, Blender blender,
            CallbackInfo callback) {
        // Explicit datapack opt-in in the unused vein-gap channel, plus native rock.
        // No third-party class file is modified on disk. Both client and server use this.
        double marker=settings.f_209353_().f_209394_().m_207386_(new DensityFunction.SinglePointContext(0,0,0));
        if (marker == -0.812345 && settings.f_64440_().toString().contains("botania:livingrock")) {
            f_188728_=new RegionalAquifer(f_188728_,state.m_224578_().f_209386_());
        }
    }
}

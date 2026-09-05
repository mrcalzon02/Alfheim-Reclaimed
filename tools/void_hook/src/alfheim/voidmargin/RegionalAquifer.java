package alfheim.voidmargin;

import net.minecraft.world.level.levelgen.Aquifer;
import net.minecraft.world.level.levelgen.DensityFunction;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;

/** SRG names deliberately match the pinned Forge 1.20.1 runtime. */
public final class RegionalAquifer implements Aquifer {
    private final Aquifer delegate;
    private final DensityFunction continentalness;
    private boolean dry;
    public RegionalAquifer(Aquifer delegate, DensityFunction continentalness) {
        this.delegate=delegate;
        this.continentalness=continentalness;
    }
    @Override public BlockState m_207104_(DensityFunction.FunctionContext context, double density) {
        dry=continentalness.m_207386_(context)<-0.80;
        if (dry) return density>0 ? null : Blocks.f_50016_.m_49966_();
        return delegate.m_207104_(context,density);
    }
    @Override public boolean m_142203_() { return !dry && delegate.m_142203_(); }
}

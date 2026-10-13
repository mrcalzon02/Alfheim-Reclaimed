package com.continuityworks.alfheimcompanion.worldgen;

/** Derived from tools/harbor_complex_layout.json; coordinates rotate about template origin. */
public final class HarborGeometry {
    public record Part(String name, int x, int z, int rotation, int minX, int minZ, int maxX, int maxZ) {
        public boolean maritime() { return name.equals("wavebreak_pier") || name.equals("sunken_drydock"); }
    }
    public static final Part[] PARTS = {
        new Part("harbor_exchange", 0, 0, 0, 0, 0, 46, 46),
        new Part("bonded_warehouse", -47, 42, 3, -47, 4, -1, 42),
        new Part("wavebreak_pier", 0, -39, 0, 0, -39, 46, -1),
        new Part("quay_court", 46, 77, 2, 0, 47, 46, 77),
        new Part("harbormaster_house", 93, 4, 1, 47, 4, 93, 42),
        new Part("tide_temple", -78, 42, 3, -78, 4, -48, 42),
        new Part("sunken_drydock", 0, -70, 0, 0, -70, 46, -40),
        new Part("signal_lighthouse", 77, 47, 1, 47, 47, 77, 77),
        new Part("harbor_approach", 34, 109, 2, 12, 78, 34, 109),
        new Part("dockworker_housing", -31, 81, 3, -31, 43, -1, 81)
    };
    public static int[] rotate(int x, int z, int r) {
        for (int i=0;i<r;i++) { int t=x; x=-z; z=t; }
        return new int[]{x,z};
    }
    private HarborGeometry() {}
}

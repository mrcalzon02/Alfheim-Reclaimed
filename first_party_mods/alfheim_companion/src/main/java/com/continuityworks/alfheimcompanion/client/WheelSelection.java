package com.continuityworks.alfheimcompanion.client;

/** Pure input geometry for the companion command wheel; no client or network dependencies. */
public final class WheelSelection {
    private WheelSelection() {}

    /**
     * @return nearest clockwise action index, starting at twelve o'clock, or -1 to cancel.
     */
    public static int index(double dx, double dy, int actionCount,
                            double deadZoneRadius, double outerRadius) {
        if (actionCount < 1 || deadZoneRadius < 0 || outerRadius <= deadZoneRadius
                || !Double.isFinite(dx) || !Double.isFinite(dy)
                || !Double.isFinite(deadZoneRadius) || !Double.isFinite(outerRadius)) return -1;

        double squared = dx * dx + dy * dy;
        if (squared < deadZoneRadius * deadZoneRadius || squared > outerRadius * outerRadius)
            return -1;

        double fullCircle = Math.PI * 2.0;
        double sector = fullCircle / actionCount;
        double clockwise = Math.atan2(dy, dx) + Math.PI / 2.0;
        if (clockwise < 0) clockwise += fullCircle;
        return ((int) Math.floor((clockwise + sector / 2.0) / sector)) % actionCount;
    }
}

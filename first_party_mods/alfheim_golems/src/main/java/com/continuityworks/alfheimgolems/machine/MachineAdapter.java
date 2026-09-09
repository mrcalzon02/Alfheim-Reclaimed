package com.continuityworks.alfheimgolems.machine;

import com.continuityworks.alfheimgolems.order.EndpointRef;
import com.continuityworks.alfheimgolems.order.FailureReason;
import net.minecraft.server.level.ServerLevel;

/** Explicit opt-in contract for a supported processing machine family. */
public interface MachineAdapter {
    String adapterId();

    boolean supports(ServerLevel level, EndpointRef endpoint);

    MachineInspection inspect(ServerLevel level, EndpointRef endpoint);

    record MachineInspection(boolean canAcceptInput, boolean processing, boolean outputAvailable,
                             FailureReason failureReason) {
        public MachineInspection {
            if (failureReason == null) failureReason = FailureReason.INTERNAL_ERROR;
        }

        public static MachineInspection unsupported() {
            return new MachineInspection(false, false, false, FailureReason.UNSUPPORTED_MACHINE);
        }
    }
}

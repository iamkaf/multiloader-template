package com.example.template;

import com.example.template.platform.Services;

/**
 * Common entry point for the Template mod.
 */
public final class TemplateMod {

    private TemplateMod() {
    }

    /**
     * Called during mod initialization for all loaders.
     */
    public static void init() {
        Constants.LOG.info("Initializing {} on {}...", Constants.MOD_NAME, Services.PLATFORM.getPlatformName());

        // AmberInitializer does not exist on 1.20.1-era Amber.
        // Amber is available purely as an API dependency here; no explicit init call.
    }
}

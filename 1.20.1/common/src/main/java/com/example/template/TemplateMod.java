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
        Constants.info("Initializing " + Constants.MOD_NAME + " on " + Services.PLATFORM.getPlatformName() + "...");

        // Amber initialization changed across MC versions.
        // - Newer: com.iamkaf.amber.api.core.v2.AmberInitializer#initialize(String)
        // - Older: no explicit initializer class (Amber is just used as an API dependency)
        try {
            Class<?> initializer = Class.forName("com.iamkaf.amber.api.core.v2.AmberInitializer");
            initializer.getMethod("initialize", String.class).invoke(null, Constants.MOD_ID);
        } catch (ClassNotFoundException ignored) {
            // No-op on older Amber versions.
        } catch (ReflectiveOperationException e) {
            throw new RuntimeException("Failed to initialize Amber", e);
        }
    }
}

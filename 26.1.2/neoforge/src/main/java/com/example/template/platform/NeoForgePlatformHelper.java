package com.example.template.platform;

import com.example.template.platform.services.IPlatformHelper;
import net.neoforged.fml.ModList;
import net.neoforged.fml.loading.FMLLoader;
import net.neoforged.fml.loading.FMLPaths;

public class NeoForgePlatformHelper implements IPlatformHelper {

    @Override
    public String getPlatformName() {
        return "NeoForge";
    }

    @Override
    public boolean isModLoaded(String modId) {
        return ModList.get().isLoaded(modId);
    }

    @Override
    public boolean isDevelopmentEnvironment() {
        // In newer NeoForge/FML, isProduction() is an instance method.
        // getCurrentOrNull() keeps this safe for unusual early-init/unit-test contexts.
        var loader = FMLLoader.getCurrentOrNull();
        return loader == null || !loader.isProduction();
    }

    @Override
    public java.nio.file.Path getConfigDirectory() {
        return FMLPaths.CONFIGDIR.get();
    }
}

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
        // NeoForge/FML API differs by version:
        // - newer: FMLLoader is instance + getCurrentOrNull()
        // - older (1.21.1 era): FMLLoader.isProduction() is static
        return !FMLLoader.isProduction();
    }

    @Override
    public java.nio.file.Path getConfigDirectory() {
        return FMLPaths.CONFIGDIR.get();
    }
}

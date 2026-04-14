package com.example.template.platform;

import com.example.template.platform.services.IPlatformHelper;
//? if >=26.1 {
import net.minecraftforge.fml.loading.LoadingModList;
//?} else {
import net.minecraftforge.fml.ModList;
//?}
import net.minecraftforge.fml.loading.FMLLoader;
import net.minecraftforge.fml.loading.FMLPaths;

public class ForgePlatformHelper implements IPlatformHelper {

    @Override
    public String getPlatformName() {
        return "Forge";
    }

    @Override
    public boolean isModLoaded(String modId) {
//? if >=26.1 {
        return LoadingModList.getModFileById(modId) != null;
//?} else {
        return ModList.get().isLoaded(modId);
//?}
    }

    @Override
    public boolean isDevelopmentEnvironment() {
        return !FMLLoader.isProduction();
    }

    @Override
    public java.nio.file.Path getConfigDirectory() {
        return FMLPaths.CONFIGDIR.get();
    }
}

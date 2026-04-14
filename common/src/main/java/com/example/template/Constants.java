package com.example.template;

//? if >=1.21.11 {
import net.minecraft.resources.Identifier;
//?} else {
import net.minecraft.resources.ResourceLocation;
//?}
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public final class Constants {
    public static final String MOD_ID = "template";
    public static final String MOD_NAME = "Template";
    public static final Logger LOG = LoggerFactory.getLogger(MOD_NAME);

    private Constants() {
    }

    public static void logInfo(String message, Object... args) {
        LOG.info(message, args);
    }

    public static void logDebug(String message, Object... args) {
        LOG.debug(message, args);
    }

//? if >=1.21.11 {
    public static Identifier resource(String path) {
        return Identifier.fromNamespaceAndPath(MOD_ID, path);
    }
//?} elif >=1.21.1 {
    public static ResourceLocation resource(String path) {
        return ResourceLocation.fromNamespaceAndPath(MOD_ID, path);
    }
//?} else {
    public static ResourceLocation resource(String path) {
        return new ResourceLocation(MOD_ID, path);
    }
//?}
}

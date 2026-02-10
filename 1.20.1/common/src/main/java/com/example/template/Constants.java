package com.example.template;

/**
 * Keep common code for 1.20.1 free of direct Minecraft classes.
 * (This version doesn't use NeoForm in :common, so MC types aren't on the compile classpath.)
 */
public final class Constants {
    public static final String MOD_ID = "template";
    public static final String MOD_NAME = "Template";

    private Constants() {
    }

    public static void info(String msg) {
        System.out.println("[" + MOD_NAME + "/INFO] " + msg);
    }

    public static void debug(String msg) {
        System.out.println("[" + MOD_NAME + "/DEBUG] " + msg);
    }
}

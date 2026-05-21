package com.example.template;

public final class Constants {
    public static final String MOD_ID = "template";
    public static final String MOD_NAME = "Template";

    private Constants() {
    }

    public static void logInfo(String message, Object... args) {
        System.out.println("[INFO] [" + MOD_NAME + "] " + format(message, args));
    }

    public static void logDebug(String message, Object... args) {
        System.out.println("[DEBUG] [" + MOD_NAME + "] " + format(message, args));
    }

    private static String format(String message, Object... args) {
        String formatted = message;
        for (Object arg : args) {
            formatted = formatted.replaceFirst("\\{}", String.valueOf(arg));
        }
        return formatted;
    }
}

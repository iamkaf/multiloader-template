package com.example.modtemplate;

import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.event.player.UseEntityCallback;

/**
 * Fabric entry point.
 */
public class TemplateFabric implements ModInitializer {

    @Override
    public void onInitialize() {
        TemplateMod.init();

        UseEntityCallback.EVENT.register((player, level, hand, entity, hitResult) ->
                TemplateMod.onPlayerEntityInteract(player, level, hand, entity));
    }
}

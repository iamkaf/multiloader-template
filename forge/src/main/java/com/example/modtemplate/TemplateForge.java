package com.example.modtemplate;

import net.minecraft.world.InteractionResult;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import static net.minecraft.world.InteractionResult.*;

@Mod(Constants.MOD_ID)
public class TemplateForge {

    public TemplateForge() {
        TemplateMod.init();

        MinecraftForge.EVENT_BUS.register(EventHandlerCommon.class);
    }

    static class EventHandlerCommon {
        @SubscribeEvent(priority = EventPriority.HIGH)
        public static void event(PlayerInteractEvent.EntityInteract event) {
            InteractionResult result = TemplateMod.onPlayerEntityInteract(
                    event.getEntity(),
                    event.getLevel(),
                    event.getHand(),
                    event.getTarget()
            );
        }
    }
}
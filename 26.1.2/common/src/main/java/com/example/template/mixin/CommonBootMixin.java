package com.example.template.mixin;

import com.example.template.Constants;
import net.minecraft.client.Minecraft;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(Minecraft.class)
public abstract class CommonBootMixin {

    @Inject(method = "<init>", at = @At("TAIL"))
    private void template$logCommonBoot(CallbackInfo callbackInfo) {
        Constants.LOG.info("[{}] Common mixin initialized during Minecraft client boot", Constants.MOD_ID);
    }
}

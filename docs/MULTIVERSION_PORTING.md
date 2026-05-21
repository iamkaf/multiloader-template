# Make A Mod Work Everywhere

These are the build and runtime notes that matter when taking a workspace mod across the full Stonecutter version matrix. Treat this as a portability checklist, not a changelog.

## Version Discovery

- Add one `versions/<mc>/gradle.properties` file per Minecraft line.
- Keep the version file as the source of truth for:
  - `project.minecraft`
  - `project.java`
  - `project.build-java`
  - `project.enabled-loaders`
  - loader version ranges
  - mixin compatibility values
- Do not add per-version Gradle projects by hand. Let Stonecutter and the workspace conventions discover `versions/<mc>/gradle.properties`.
- Keep loader availability aligned with `~/code/mods/version-catalog/mc-<mc>/gradle/libs.versions.toml`. If a catalog has no Forge or NeoForge version for a line, do not enable that loader.

## Loader Matrix

Use this shape unless the mod has a specific reason to differ:

- Fabric starts at the oldest supported Minecraft line.
- Forge starts at `1.16.5` only when the mod really needs legacy Forge; otherwise prefer `1.17+`.
- NeoForge starts at `1.21.1+` unless the catalog and mod explicitly support an earlier line.
- `1.20.5` is usually Fabric-only in this workspace.
- `1.21.2` is usually Fabric + NeoForge only because Forge is absent from the shared catalog.
- Modern `26.x` lines use the non-`1.x` Minecraft version naming and should stay aligned with the catalog.

## Java And Mixin Compatibility

- Match `project.java` and `project.build-java` to the line's loader toolchain, not to the newest JDK installed locally.
- Use Java 16 for legacy `1.14.4` through `1.17.1` lines when the loader/runtime requires it.
- Use Java 17 for `1.18` through most `1.20.x` lines.
- Use Java 21 for modern `1.20.5+`, `1.21+`, and `26.x` lines where the loader supports it.
- Keep mixin compatibility no higher than the bundled Mixin version can parse.
  - Some Forge lines that run on Java 21 still need `JAVA_17` in mixin JSON.
  - Use resource placeholders such as `${mixin_compat_common}`, `${mixin_compat_fabric}`, `${mixin_compat_forge}`, and `${mixin_compat_neoforge}` so each version line controls its own value.

## Fabric Build Rules

- Use `modImplementation` and `modLocalRuntime` for obfuscated `1.x` Fabric lines.
- Use plain `implementation` and `runtimeOnly` for non-obfuscated modern `26.x` Fabric lines when the project shape requires it.
- Older Fabric runtime metadata often does not expose the umbrella `fabric-api` mod id.
  - For `1.14.4`, `1.15.x`, `1.16.2` through `1.16.5`, `1.17.x`, `1.18`, and `1.18.1`, rewrite `fabric.mod.json` dependencies from `fabric-api` to `fabric`.
  - For `1.16` and `1.16.1`, replace the umbrella dependency with the exact Fabric API modules the mod needs.
  - For `1.19` and `1.19.1`, replace the umbrella dependency with concrete module ids when Loom exposes modules but not the umbrella mod.
- Legacy Fabric lines may need explicit runtime logging jars so boot checks can observe log markers:
  - `org.slf4j:slf4j-api`
  - `org.slf4j:slf4j-simple`

## Forge Build Rules

- Forge `1.16.5` is a build island. Expect custom run wiring.
  - Use Java 16 for the dev launcher.
  - Provide legacy Forge userdev and launcher jars on the run classpath.
  - Stage LWJGL natives explicitly.
  - Set asset, native, MCP, Forge, and launch-target environment values explicitly.
  - Use a custom `runLegacyClient` task when normal `runClient` cannot launch the line.
  - Strip or rewrite generated `mods.toml` dependency ranges that old Forge cannot parse.
- Forge `1.17.1` needs legacy ModDev run patching.
  - Patch `{runtime_classpath}` and `{natives}` placeholders in generated run args.
  - Run with the Java 16 launcher.
  - Extract LWJGL natives.
  - Exclude incompatible bootstrap or securejarhandler jars from the patched classpath when needed.
  - Add `--add-opens=java.base/java.lang.invoke=cpw.mods.securejarhandler`.
- Forge `1.18`, `1.18.1`, and `1.19` commonly need:
  - `org.slf4j:slf4j-simple` at runtime
  - `--add-opens=java.base/java.lang.invoke=cpw.mods.securejarhandler`
- Older Forge ModDev runtimes may need runtime helper mods staged from local dev-compiled output rather than published jars, because published jars can be remapped for a different namespace than the dev runtime.
- Keep these legacy Forge hacks isolated in `forge/build.gradle` until they can move into `multiloader-conventions`.

## NeoForge Build Rules

- Keep NeoForge loader ranges tied to the `javafml` language-loader version reported by the target NeoForge line.
- Check newer NeoForge loader helpers when crossing minor `1.21.x` lines; loader methods may move from static calls to instance access.
- Prefer the shared catalog for NeoForge coordinates and avoid ad hoc pins in mod repos.

## TeaKit Runtime Checks

- Add `teakitw` and `teakit.toml` to mods that need repeatable runtime verification.
- Use TeaKit boot checks for every enabled loader/version node.
- For normal lines, require:
  - the mod's initialization marker
  - TeaKit startup
  - TeaKit title-screen auto-exit
- For legacy lines where TeaKit does not support title auto-exit, use a bounded boot marker that proves the client reached the title-resource phase.
- Do not leave Gradle or client processes running after boot probes.

## Shared Conventions

- Push repeated build behavior into `~/code/mods/multiloader-conventions`.
- Good candidates for conventions:
  - Stonecutter version discovery
  - Fabric legacy dependency-id replacement
  - Fabric legacy module selection
  - Forge legacy run-client strategies
  - TeaKit runtime dependency/staging
  - Java and mixin compatibility defaults
- Keep one-off Gradle islands only when a version line truly needs them.

## Publishing And CI

- Keep version files discoverable by `just`, CI, and publishing workflows.
- Validate each enabled node independently.
- Publish workspace library/helper changes to Maven local during development only.
- Do not publish to Kaf Maven from agent workflows.
- Before release, confirm the matrix against:
  - local boot checks
  - shared version catalog coordinates
  - Kaf Maven publishing state
  - platform release requirements

## Practical Order

1. Add the version files and loader matrix.
2. Align Java, build Java, mixin compatibility, and loader ranges.
3. Fix Fabric metadata and legacy module wiring.
4. Fix Forge runtime islands from oldest to newest.
5. Add TeaKit boot checks.
6. Run the full matrix.
7. Move repeated fixes into conventions once at least two projects need them.

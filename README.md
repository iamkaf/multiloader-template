# Template

A branch-based Stonecutter multi-loader Minecraft mod template.

The template is intentionally thin. The root build, project graph, and loader setup come from `multiloader-conventions`, so this repo mostly contains source, version metadata, and small workflow wrappers.

## Quick Start

Build everything:

```bash
./gradlew build
```

List supported nodes:

```bash
just list-nodes
```

Build one node:

```bash
just build 1.21.11-forge
```

Run one node:

```bash
just run-client 1.21.10-fabric
```

Run version- or loader-scoped Gradle tasks through the compatibility wrapper:

```bash
just run downloadTranslations
just run 1.21.11 publishMod -Ppublish.dry-run=true
just run 1.21.11 forge publishModrinth -Ppublish.dry-run=true
just run 1.21.11 forge runClient
```

Run a TeaKit-backed smoke check on one node:

```bash
just teakit-boot-check 1.21.11-forge 60
```

Validate the whole matrix:

```bash
just build-all
just boot-check-all 80
just teakit-boot-check-all 60
```

`boot-check-all` starts each client, waits up to the given timeout in seconds, and checks the logs for the expected startup markers.
`teakit-boot-check-all` injects TeaKit from the shared version catalog at runtime and relies on TeaKit's title-screen auto-exit for a fast clean shutdown.
Those TeaKit checks expect the matching TeaKit artifacts for each node to exist in `mavenLocal`.

## Layout

Shared source lives in the stable loader projects:

- `common/`
- `fabric/`
- `forge/`
- `neoforge/`

Version-specific configuration and overrides live in `versions/<mc-version>/`:

- `gradle.properties` for version identity, Java toolchain, loader matrix, and version ranges
- `common/src/main/...` for shared version-specific overrides
- `<loader>/src/main/...` for loader-specific version-specific overrides

Stonecutter exposes those as versioned projects:

- `:common:<mc-version>`
- `:fabric:<mc-version>`
- `:forge:<mc-version>`
- `:neoforge:<mc-version>`

Generated branch workdirs live under:

- `common/versions/`
- `fabric/versions/`
- `forge/versions/`
- `neoforge/versions/`

Those directories are build output and are ignored by Git. Version-local build output under `versions/<mc-version>/build/` is ignored too.

## Common

`common` is a real standalone artifact, not just an abstract source bucket.

- `:common:<mc-version>` builds on its own
- loader projects consume the generated `common` sources and resources for the same Minecraft line
- `common` can reference Minecraft classes directly

The standalone common build is version-aware:

- `1.20.1` uses the LegacyForge-backed path
- `1.21.1+` uses the NeoForm / ModDev path

## Supported Nodes

- `1.20.1-fabric`
- `1.20.1-forge`
- `1.21.1-fabric`
- `1.21.1-forge`
- `1.21.1-neoforge`
- `1.21.10-fabric`
- `1.21.10-forge`
- `1.21.10-neoforge`
- `1.21.11-fabric`
- `1.21.11-forge`
- `1.21.11-neoforge`
- `26.1-fabric`
- `26.1-forge`
- `26.1-neoforge`
- `26.1.1-fabric`
- `26.1.1-forge`
- `26.1.1-neoforge`
- `26.1.2-fabric`
- `26.1.2-forge`
- `26.1.2-neoforge`

## Workflow Notes

- `./gradlew build` is the canonical root build
- `just build-all` intentionally maps to that root build
- `just run <version> <loader> <task>` is the compatibility wrapper for node-scoped Gradle tasks
- `just teakit-boot-check <node>` runs the node with:
  - `-Dtemplate.withTeaKit=true`
  - `-Dteakit.autoExitTitle=true`
  - `-Dteakit.autoExitTitleDelayMs=2500`
- `just projects` is useful when checking the generated Stonecutter project graph
- `just clean-generated` removes generated branch workdirs and version-local build output

Examples:

```bash
just run 1.21.11 forge build
just run 26.1.2 neoforge runClient
just run 1.21.10 publish
```

## Editing Notes

- Put loader-agnostic code in `common/`.
- Use `versions/<mc-version>/common/` when a Minecraft line needs a shared override.
- Use `versions/<mc-version>/<loader>/` when only one loader on one line differs.
- Update `versions/<mc-version>/gradle.properties` when adding a new line or changing version-specific metadata.
- Prefer Stonecutter preprocess guards for small API drift instead of duplicating whole files.

The build entrypoints should stay thin:

- [settings.gradle.kts](settings.gradle.kts)
- [stonecutter.gradle.kts](stonecutter.gradle.kts)
- `common/build.gradle`
- `fabric/build.gradle`
- `forge/build.gradle`
- `neoforge/build.gradle`

## Status

This template has been verified to:

- build from the root with `./gradlew build`
- build every supported node
- boot a client on every supported node

## License

Licensed under the MIT License. See [LICENSE](LICENSE).

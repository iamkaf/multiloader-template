# Template

A Stonecutter-based multi-loader Minecraft mod template.

This repo is meant to stay small at the top level. Most build logic lives in the `multiloader-conventions` plugins, so the template mostly contains source, version data, and thin Gradle entrypoints.

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

Validate the whole matrix:

```bash
just build-all
just boot-check-all 80
```

`boot-check-all` starts each client, waits up to the given timeout in seconds, and checks that startup reached the expected client path.

## Layout

Shared source lives in:

- `common/`
- `fabric/`
- `forge/`
- `neoforge/`

Version-specific configuration and overrides live in `versions/<mc-version>/`:

- `gradle.properties` for metadata, Java version, and enabled loaders
- `common/src/main/...` for shared version-specific overrides
- `<loader>/src/main/...` for loader-specific version-specific overrides

Stonecutter exposes those as versioned projects:

- `:common:<mc-version>`
- `:fabric:<mc-version>`
- `:forge:<mc-version>`
- `:neoforge:<mc-version>`

Generated branch workdirs live under `common/versions/`, `fabric/versions/`, `forge/versions/`, and `neoforge/versions/`. They are build output and are ignored by Git.

## Common

`common` is a real standalone artifact.

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

## Editing Notes

- Put loader-agnostic code in `common/`.
- Use `versions/<mc-version>/common/` when a Minecraft line needs a shared override.
- Use `versions/<mc-version>/<loader>/` when only one loader on one line differs.
- Update `versions/<mc-version>/gradle.properties` when adding a new line or changing version-specific metadata.
- Prefer Stonecutter preprocess guards for small API drift instead of duplicating whole files.

The root entrypoints are intentionally thin:

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

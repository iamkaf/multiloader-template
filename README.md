# Template

A reusable multi-loader Minecraft mod template built around Stonecutter.

## Layout

This repository uses a branch-based Stonecutter layout.

Shared code lives in:

- `common/`
- `fabric/`
- `forge/`
- `neoforge/`

Version-specific configuration and overlays live in `versions/<mc-version>/`:

- `gradle.properties` for metadata and toolchain settings
- `common/src/main/...` for shared per-version overrides
- `<loader>/src/main/...` for loader-specific per-version overrides

Stonecutter exposes those as versioned subprojects:

- `:common:<mc-version>`
- `:fabric:<mc-version>`
- `:forge:<mc-version>`
- `:neoforge:<mc-version>`

Generated branch workdirs live under `common/versions/`, `fabric/versions/`, `forge/versions/`, and `neoforge/versions/`. They are build output and ignored by Git.

## Common Artifact

`common` is a real standalone artifact, not just a source bucket.

- `:common:<mc-version>` builds on its own
- loader projects consume the generated `common` sources/resources for the same Minecraft line
- `common` can reference Minecraft classes directly

The standalone `common` build uses the same style as the library mods in this workspace:

- `1.20.1`: LegacyForge-backed common artifact
- `1.21.1+`: NeoForm / ModDev-backed common artifact

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

## Common Workflow

Build the whole repo from the root:

```bash
./gradlew build
```

Show the generated project graph:

```bash
just projects
```

List nodes:

```bash
just list-nodes
```

Build a specific node:

```bash
just build 1.21.11-forge
```

Run a specific node:

```bash
just run-client 1.21.10-fabric
```

Validate the full matrix:

```bash
just build-all
just boot-check-all 80
```

`boot-check-all` launches each client, waits up to the given timeout in seconds, and verifies that the game reached the client render path before terminating it.

Delete generated Stonecutter branch workdirs:

```bash
just clean-generated
```

## Editing Guidance

- Put loader-agnostic code in `common/`.
- Use `versions/<mc-version>/common/` when a Minecraft line needs a shared override.
- Use `versions/<mc-version>/<loader>/` when only one loader on one line diverges.
- Update `versions/<mc-version>/gradle.properties` when adding a new line or changing metadata.
- Prefer Stonecutter preprocess guards for small API drift instead of duplicating whole files.

## Validation Status

The current Stonecutter port has been verified to:

- build from the root with `./gradlew build`
- build every supported loader/version node
- boot a client on every supported node

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

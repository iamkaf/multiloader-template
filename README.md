# Multi-loader Mod Template

This repository provides a basic template for creating Minecraft mods that target Fabric, Forge and NeoForge from the same codebase.
It is adapted from [jaredlll08's MultiLoader-Template](https://github.com/jaredlll08/MultiLoader-Template) and stripped down to a minimal starting point.
The original template repository lives at [iamkaf/template-mod](https://github.com/iamkaf/template-mod).

## Getting started

1. Clone this repository.
2. Run `python scripts/moddy.py setup` and answer the prompts. The script will
   ask for your base package, mod id, name, author and initial version then
   update packages, class names and identifiers accordingly, and insert the
   version into `changelog.md`.
3. When bumping to a new Minecraft version, run `python scripts/moddy.py set-minecraft-version <version>` to pull matching dependency versions.
4. Replace the placeholder code in `TemplateMod` with your own logic.
5. Run the Gradle `build` task to produce jars for each loader.

## Directory layout

- `common/` contains code shared between all loaders.
- `fabric/`, `forge/` and `neoforge/` contain loader specific entry points and build logic.
- `buildSrc/` holds the Gradle scripts that wire everything together.

Feel free to expand upon this structure to suit the needs of your own mods.

## Adding a new service

Add a new platform service with `python scripts/moddy.py add-service <ServiceName>`.

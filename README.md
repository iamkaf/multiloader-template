# Template

A reusable multi-loader Minecraft mod template with Amber integration.

![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ About

This repo is a minimal, reusable mod template built for Fabric, Forge, and NeoForge. It keeps the multi-loader setup intact, includes Amber as a dependency, and strips all gameplay content so you can start fresh.

## 🗂️ Monorepo Structure

```
multiloader-template/
├── 1.21.10/         # Minecraft 1.21.10 version
│   ├── common/      # Shared code across loaders
│   ├── fabric/      # Fabric-specific implementation
│   ├── forge/       # Forge-specific implementation
│   └── neoforge/    # NeoForge-specific implementation
├── 1.21.11/         # Minecraft 1.21.11 version
│   ├── common/
│   ├── fabric/
│   ├── forge/
│   └── neoforge/
└── README.md        # This file
```

## ✅ Supported Versions

| Minecraft Version | Status | Directory |
|-------------------|--------|-----------|
| 1.20.1           | ✅ Active | `1.20.1/` |
| 1.21.1           | ✅ Active | `1.21.1/` |
| 1.21.10           | ✅ Active | `1.21.10/` |
| 1.21.11           | ✅ Active | `1.21.11/` |

## 🚀 Getting Started

1. Pick a version folder (e.g. `1.21.11/`) and open it in your IDE.
2. Update `gradle.properties` with your mod info:
   - `project.*` for version/build coordinates
   - `mod.*` for metadata
   - `publish.*`, `dependencies.*`, and `environments.*` for release settings
3. Update package names from `com.example.template` to your own group.
4. Add your content in `common/src/main/java` and `common/src/main/resources`.

## 🛠️ Building

Use `just` from the repo root as the command runner.

```bash
# Build all loaders for a specific version
just build 1.21.11

# Build all loaders across all versions
just build

# Build a specific loader for a specific version
just run 1.21.11 :fabric:build
just run 1.21.11 :forge:build
just run 1.21.11 :neoforge:build

# Run tests
just test 1.21.11
just test
```

Built jars will be in `<version>/<loader>/build/libs/`.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links (placeholders)

- **CurseForge**: https://www.curseforge.com/minecraft/mc-mods/your-mod
- **Modrinth**: https://modrinth.com/mod/your-mod
- **Issues**: https://github.com/example/template/issues

## 🙏 Acknowledgments

- Based on jaredlll08's MultiLoader-Template

import java.util.Properties

pluginManagement {
    repositories {
        mavenLocal()
        gradlePluginPortal()
        mavenCentral()
        maven("https://maven.fabricmc.net")
        maven("https://maven.minecraftforge.net")
        maven("https://maven.neoforged.net/releases")
        maven("https://repo.spongepowered.org/repository/maven-public")
        maven("https://maven.firstdarkdev.xyz/releases")
        maven("https://maven.kaf.sh")
    }

    plugins {
        id("fabric-loom") version "1.15-SNAPSHOT"
        id("net.fabricmc.fabric-loom") version "1.15-SNAPSHOT"
        id("net.minecraftforge.gradle") version "7.0.17"
        id("net.neoforged.moddev") version "2.0.141"
        id("net.neoforged.moddev.legacyforge") version "2.0.140"
        id("org.spongepowered.mixin") version "0.7-SNAPSHOT"
    }
}

plugins {
    id("org.gradle.toolchains.foojay-resolver-convention") version "1.0.0"
    id("dev.kikugie.stonecutter") version "0.7.10"
}

fun loadVersionProperties(version: String): Properties {
    val propertiesFile = file("versions/$version/gradle.properties")
    require(propertiesFile.isFile) { "Missing version properties: ${propertiesFile.path}" }

    return Properties().apply {
        propertiesFile.inputStream().use(::load)
    }
}

val versionDirs = file("versions")
    .listFiles()
    ?.filter { it.isDirectory && file("versions/${it.name}/gradle.properties").isFile }
    ?.sortedBy { it.name }
    .orEmpty()

require(versionDirs.isNotEmpty()) { "No version definitions found under versions/" }

val versionsWithLoaders = linkedMapOf<String, List<String>>()
for (dir in versionDirs) {
    val version = dir.name
    val props = loadVersionProperties(version)
    val loaders = props.getProperty("project.enabled-loaders")
        ?.split(',')
        ?.map(String::trim)
        ?.filter(String::isNotEmpty)
        .orEmpty()

    require(loaders.isNotEmpty()) { "No enabled loaders configured for $version" }
    versionsWithLoaders[version] = loaders
}

val uniqueVersions = versionsWithLoaders.keys.toList()
val fabricVersions = versionsWithLoaders.filterValues { "fabric" in it }.keys.toTypedArray()
val forgeVersions = versionsWithLoaders.filterValues { "forge" in it }.keys.toTypedArray()
val neoforgeVersions = versionsWithLoaders.filterValues { "neoforge" in it }.keys.toTypedArray()

dependencyResolutionManagement {
    repositories {
        mavenLocal()
        maven("https://maven.kaf.sh")
        mavenCentral()
    }

    versionCatalogs {
        uniqueVersions.forEach { version ->
            create("libsMc${version.replace(".", "").replace("-", "")}") {
                from(files("../version-catalog/mc-$version/gradle/libs.versions.toml"))
            }
        }
    }
}

rootProject.name = providers.gradleProperty("mod.name").orNull
    ?: loadVersionProperties(uniqueVersions.first()).getProperty("mod.name")
    ?: "Template"

stonecutter {
    create(rootProject) {
        versions(*uniqueVersions.toTypedArray())

        branch("common") {
            versions(*uniqueVersions.toTypedArray())
        }
        branch("fabric") {
            versions(*fabricVersions)
        }
        branch("forge") {
            versions(*forgeVersions)
        }
        branch("neoforge") {
            versions(*neoforgeVersions)
        }
    }
}

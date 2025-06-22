#!/usr/bin/env python3
"""Update gradle.properties with dependency versions for a Minecraft version."""
import argparse
import json
import re
import sys
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path


def fetch_url_text(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode("utf-8")


def get_artifact_latest(meta_url, mc_version):
    """Return the newest version for the given MC prefix from a Maven metadata.xml."""
    try:
        xml_text = fetch_url_text(meta_url)
    except Exception:
        return None

    versions = re.findall(r"<version>([^<]+)</version>", xml_text)
    prefix = mc_version + "-"
    candidates = [v for v in versions if v.startswith(prefix)]
    if not candidates:
        return None

    # Prefer final releases over -rc or -pre builds
    stable = [v for v in candidates if "-rc" not in v and "-pre" not in v]
    versions = stable if stable else candidates
    versions.sort()
    return versions[-1]


def get_neoform_version(mc):
    url = (
        "https://maven.neoforged.net/releases/net/neoforged/neoform/maven-metadata.xml"
    )
    return get_artifact_latest(url, mc)


def get_neoforge_version(mc):
    """Resolve the highest NeoForge version matching the Minecraft release."""
    meta_url = (
        "https://maven.neoforged.net/releases/net/neoforged/neoforge/maven-metadata.xml"
    )
    try:
        xml_text = fetch_url_text(meta_url)
    except Exception:
        return None

    root = ET.fromstring(xml_text)
    mc_prefix = ".".join(mc.split(".")[1:3])  # e.g. 21.5 from 1.21.5
    versions = [
        v.text
        for v in root.findall("./versioning/versions/version")
        if v.text.startswith(mc_prefix)
    ]
    if not versions:
        return None

    stable = [v for v in versions if "-beta" not in v and "-rc" not in v]
    versions = stable if stable else versions
    return versions[-1]


def get_parchment_version(mc):
    url = f"https://maven.parchmentmc.org/org/parchmentmc/data/parchment-{mc}/maven-metadata.xml"
    try:
        xml_text = fetch_url_text(url)
        root = ET.fromstring(xml_text)
        return root.findtext("versioning/latest")
    except Exception:
        return None


def get_fabric_loader_version(mc):
    url = f"https://meta.fabricmc.net/v2/versions/loader/{mc}"
    try:
        data = json.loads(fetch_url_text(url))
        stable = [e["loader"]["version"] for e in data if e["loader"].get("stable")]
        if stable:
            def ver_key(v):
                return [int(x) if x.isdigit() else x for x in re.split(r"[.-]", v)]
            return sorted(stable, key=ver_key)[-1]
    except Exception:
        pass
    return None


def get_fabric_api_version(mc):
    query = urllib.parse.quote(f'["{mc}"]', safe="")
    url = f"https://api.modrinth.com/v2/project/fabric-api/version?game_versions={query}"
    try:
        versions = json.loads(fetch_url_text(url))
        latest = max(versions, key=lambda v: v["date_published"])
        return latest["version_number"]
    except Exception:
        return None


def get_mod_menu_version(mc):
    query = urllib.parse.quote(f'["{mc}"]', safe="")
    url = f"https://api.modrinth.com/v2/project/modmenu/version?game_versions={query}"
    try:
        versions = json.loads(fetch_url_text(url))
        latest = max(versions, key=lambda v: v["date_published"])
        return latest["version_number"]
    except Exception:
        return None


def get_forge_version(mc):
    url = f"https://files.minecraftforge.net/net/minecraftforge/forge/index_{mc}.html"
    try:
        html = fetch_url_text(url, headers={"User-Agent": "Mozilla/5.0"})
    except Exception:
        return None
    for label in ("Recommended", "Latest"):
        m = re.search(label + r":\s*([0-9.]+)", html)
        if m:
            return m.group(1)
    return None


def collect_versions(mc):
    return {
        "neoform_version": get_neoform_version(mc),
        "neoforge_version": get_neoforge_version(mc),
        "parchment_minecraft": mc,
        "parchment_version": get_parchment_version(mc),
        "fabric_loader_version": get_fabric_loader_version(mc),
        "fabric_version": get_fabric_api_version(mc),
        "mod_menu_version": get_mod_menu_version(mc),
        "forge_version": get_forge_version(mc),
    }


def apply_versions(props_path: Path, mc: str, versions: dict):
    text = props_path.read_text(encoding="utf-8")
    next_minor = mc.split(".")
    if len(next_minor) >= 2:
        try:
            minor = int(next_minor[1])
            next_minor[1] = str(minor + 1)
            next_minor = ".".join(next_minor[:2])
        except Exception:
            next_minor = mc
    else:
        next_minor = mc
    replacements = {
        "minecraft_version": mc,
        "minecraft_version_range": f"[{mc}, {next_minor})",
        "neo_form_version": versions.get("neoform_version"),
        "parchment_minecraft": mc,
        "parchment_version": versions.get("parchment_version"),
        "fabric_loader_version": versions.get("fabric_loader_version"),
        "fabric_version": versions.get("fabric_version"),
        "mod_menu_version": versions.get("mod_menu_version"),
        "forge_version": versions.get("forge_version"),
        "neoforge_version": versions.get("neoforge_version"),
        "game_versions": mc,
    }
    for key, value in replacements.items():
        if not value:
            continue
        text = re.sub(rf"(?m)^{re.escape(key)}=.*$", f"{key}={value}", text)
    props_path.write_text(text, encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Fetch dependency versions for a Minecraft version")
    parser.add_argument("version", help="Minecraft version, e.g. 1.21.5")
    args = parser.parse_args(argv)
    mc = args.version

    versions = collect_versions(mc)
    print("Fetched versions:")
    for k, v in versions.items():
        print(f"  {k}: {v}")

    missing = [k for k, v in versions.items() if v is None]
    if missing:
        print("\nFailed to determine:", ", ".join(missing))
        print("You can look them up manually at:")
        print("  https://projects.neoforged.net/neoforged/neoform")
        print("  https://projects.neoforged.net/neoforged/neoforge")
        print("  https://fabricmc.net/develop/")
        print("  https://files.minecraftforge.net/net/minecraftforge/forge/")
        print("  https://parchmentmc.org/docs/getting-started#choose-a-version")

    answer = input("\nApply these versions to gradle.properties? [y/N] ")
    if answer.lower().startswith("y"):
        apply_versions(Path("gradle.properties"), mc, versions)
        print("Updated gradle.properties")
    else:
        print("No changes made")


if __name__ == "__main__":
    main()

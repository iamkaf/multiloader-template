#!/usr/bin/env python3
"""Moddy - Multipurpose helper for the multiloader template.

This single script replaces the individual helper tools that previously lived in
``scripts``.  Each of the original utilities is now provided as a sub-command.
The goal is to keep maintenance simple and allow easy distribution of updates.

The available commands are:

```
add-service            - create a new service interface and implementations
open-libs              - open the build/libs folder for a given loader
set-minecraft-version  - update gradle.properties with dependency versions
setup                  - initialise the template after cloning
update                 - download and replace Moddy with the newest version
```

Run ``moddy.py help`` at any time to show the command list.
"""

import argparse
import json
import os
import platform
import re
import shutil
import struct
import subprocess
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path

# If set to True, Moddy will skip confirmation prompts.
AUTO_YES = False

# Current Moddy version. Bump this when publishing updates.
MODDY_VERSION = "0.1.0"
# URL of the latest Moddy script used by the ``update`` command.
UPDATE_URL = (
    "https://raw.githubusercontent.com/iamkaf/modresources/main/moddy/moddy.py"
)


# ---------------------------------------------------------------------------
# add-service implementation
# ---------------------------------------------------------------------------

def _parse_group(props_path: Path) -> str:
    """Return the 'group' property from a gradle.properties file."""
    text = props_path.read_text(encoding="utf-8")
    m = re.search(r"^group=(.+)$", text, re.MULTILINE)
    if not m:
        raise RuntimeError("Could not determine group property")
    return m.group(1).strip()


def cmd_add_service(args: argparse.Namespace) -> None:
    """Create a service interface and loader specific implementations."""
    # Validate and prepare names
    name = args.name.strip()
    if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name):
        raise SystemExit("Illegal characters in service name")

    group = _parse_group(Path("gradle.properties"))
    pkg_path = group.replace(".", "/")
    service_fqn = f"{group}.platform.services.{name}"

    interface_path = Path("common/src/main/java") / pkg_path / "platform" / "services" / f"{name}.java"
    fabric_impl_path = Path("fabric/src/main/java") / pkg_path / "platform" / f"Fabric{name}.java"
    forge_impl_path = Path("forge/src/main/java") / pkg_path / "platform" / f"Forge{name}.java"
    neo_impl_path = Path("neoforge/src/main/java") / pkg_path / "platform" / f"NeoForge{name}.java"

    fabric_meta = Path("fabric/src/main/resources/META-INF/services") / service_fqn
    forge_meta = Path("forge/src/main/resources/META-INF/services") / service_fqn
    neo_meta = Path("neoforge/src/main/resources/META-INF/services") / service_fqn

    # Template contents for all generated files
    files = {
        interface_path: f"package {group}.platform.services;\n\npublic interface {name} {{\n}}\n",
        fabric_impl_path: f"package {group}.platform;\n\nimport {service_fqn};\n\npublic class Fabric{name} implements {name} {{\n}}\n",
        forge_impl_path: f"package {group}.platform;\n\nimport {service_fqn};\n\npublic class Forge{name} implements {name} {{\n}}\n",
        neo_impl_path: f"package {group}.platform;\n\nimport {service_fqn};\n\npublic class NeoForge{name} implements {name} {{\n}}\n",
        fabric_meta: f"{group}.platform.Fabric{name}\n",
        forge_meta: f"{group}.platform.Forge{name}\n",
        neo_meta: f"{group}.platform.NeoForge{name}\n",
    }

    print(f"This will create a new service called '{name}'.")
    print("The following files will be created:\n")
    for path, content in files.items():
        print(f"--- {path}")
        print(content.rstrip())
        print()

    existing = [str(p) for p in files if p.exists()]
    if existing:
        print("The following files already exist and will not be overwritten:")
        for p in existing:
            print(f"  {p}")
        return

    if not AUTO_YES and input("Proceed? [y/N] ").lower() != "y":
        print("Aborted")
        return

    for path, content in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"Created {path}")


# ---------------------------------------------------------------------------
# open-libs implementation
# ---------------------------------------------------------------------------

def _open_dir(path: Path) -> None:
    """Open *path* using the default file manager."""
    system = platform.system()
    if system == "Windows":
        os.startfile(path)  # type: ignore[attr-defined]
    elif system == "Darwin":
        subprocess.run(["open", str(path)], check=False)
    else:
        subprocess.run(["xdg-open", str(path)], check=False)


def cmd_open_libs(args: argparse.Namespace) -> None:
    """Open the build/libs folder for the chosen loader."""
    # This command performs no project modification so we do not ask for
    # confirmation even when AUTO_YES is False.
    libs = Path(args.loader) / "build" / "libs"
    if not libs.is_dir():
        print(f"No libs folder found at {libs}. Run a build first.")
        return
    _open_dir(libs)


# ---------------------------------------------------------------------------
# set-minecraft-version implementation
# ---------------------------------------------------------------------------

def _fetch_url_text(url: str, headers=None) -> str:
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode("utf-8")


def _get_artifact_latest(meta_url: str, mc_version: str):
    try:
        xml_text = _fetch_url_text(meta_url)
    except Exception:
        return None
    versions = re.findall(r"<version>([^<]+)</version>", xml_text)
    prefix = mc_version + "-"
    candidates = [v for v in versions if v.startswith(prefix)]
    if not candidates:
        return None
    stable = [v for v in candidates if "-rc" not in v and "-pre" not in v]
    versions = stable if stable else candidates
    versions.sort()
    return versions[-1]


def _get_neoform_version(mc: str):
    url = (
        "https://maven.neoforged.net/releases/net/neoforged/neoform/maven-metadata.xml"
    )
    return _get_artifact_latest(url, mc)


def _get_neoforge_version(mc: str):
    meta_url = (
        "https://maven.neoforged.net/releases/net/neoforged/neoforge/maven-metadata.xml"
    )
    try:
        xml_text = _fetch_url_text(meta_url)
    except Exception:
        return None
    root = ET.fromstring(xml_text)
    mc_prefix = ".".join(mc.split(".")[1:3])
    versions = [
        v.text for v in root.findall("./versioning/versions/version") if v.text.startswith(mc_prefix)
    ]
    if not versions:
        return None
    stable = [v for v in versions if "-beta" not in v and "-rc" not in v]
    versions = stable if stable else versions
    return versions[-1]


def _get_parchment_version(mc: str):
    url = f"https://maven.parchmentmc.org/org/parchmentmc/data/parchment-{mc}/maven-metadata.xml"
    try:
        xml_text = _fetch_url_text(url)
        root = ET.fromstring(xml_text)
        return root.findtext("versioning/latest")
    except Exception:
        return None


def _get_fabric_loader_version(mc: str):
    url = f"https://meta.fabricmc.net/v2/versions/loader/{mc}"
    try:
        data = json.loads(_fetch_url_text(url))
        stable = [e["loader"]["version"] for e in data if e["loader"].get("stable")]
        if stable:
            def ver_key(v):
                return [int(x) if x.isdigit() else x for x in re.split(r"[.-]", v)]
            return sorted(stable, key=ver_key)[-1]
    except Exception:
        pass
    return None


def _get_fabric_api_version(mc: str):
    query = urllib.parse.quote(f'["{mc}"]', safe="")
    url = f"https://api.modrinth.com/v2/project/fabric-api/version?game_versions={query}"
    try:
        versions = json.loads(_fetch_url_text(url))
        latest = max(versions, key=lambda v: v["date_published"])
        return latest["version_number"]
    except Exception:
        return None


def _get_mod_menu_version(mc: str):
    query = urllib.parse.quote(f'["{mc}"]', safe="")
    url = f"https://api.modrinth.com/v2/project/modmenu/version?game_versions={query}"
    try:
        versions = json.loads(_fetch_url_text(url))
        latest = max(versions, key=lambda v: v["date_published"])
        return latest["version_number"]
    except Exception:
        return None


def _get_forge_version(mc: str):
    url = f"https://files.minecraftforge.net/net/minecraftforge/forge/index_{mc}.html"
    try:
        html = _fetch_url_text(url, headers={"User-Agent": "Mozilla/5.0"})
    except Exception:
        return None
    for label in ("Recommended", "Latest"):
        m = re.search(label + r":\s*([0-9.]+)", html)
        if m:
            return m.group(1)
    return None


def _collect_versions(mc: str):
    """Gather dependency versions for the given Minecraft version."""
    return {
        "neoform_version": _get_neoform_version(mc),
        "neoforge_version": _get_neoforge_version(mc),
        "parchment_minecraft": mc,
        "parchment_version": _get_parchment_version(mc),
        "fabric_loader_version": _get_fabric_loader_version(mc),
        "fabric_version": _get_fabric_api_version(mc),
        "mod_menu_version": _get_mod_menu_version(mc),
        "forge_version": _get_forge_version(mc),
    }


def _apply_versions(props_path: Path, mc: str, versions: dict) -> None:
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


def cmd_set_minecraft_version(args: argparse.Namespace) -> None:
    """Fetch dependency versions and optionally apply them to gradle.properties."""
    mc = args.version
    print(f"Fetching dependency versions for Minecraft {mc}.")
    if not AUTO_YES and input("Proceed? [y/N] ").lower() != "y":
        print("Aborted")
        return

    versions = _collect_versions(mc)
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
    answer = "y" if AUTO_YES else input("\nApply these versions to gradle.properties? [y/N] ")
    if answer.lower().startswith("y"):
        _apply_versions(Path("gradle.properties"), mc, versions)
        print("Updated gradle.properties")
    else:
        print("No changes made")


# ---------------------------------------------------------------------------
# setup implementation (from setup_mod.py)
# ---------------------------------------------------------------------------

RESET = "\033[0m"
GREEN = "\033[32m"
CYAN = "\033[36m"

OLD_PACKAGE = "com.example.modtemplate"
OLD_MOD_ID = "examplemod"
OLD_MOD_NAME = "Example Mod"
OLD_AUTHOR = "yourname"


def _default_version() -> str:
    try:
        text = Path("gradle.properties").read_text(encoding="utf-8")
        m = re.search(r"^version=(.*)$", text, re.MULTILINE)
        if m:
            return m.group(1).strip()
    except Exception:
        pass
    return "1.0.0"


def _to_camel(value: str) -> str:
    parts = re.split(r"[_\-\s]+", value)
    return "".join(p[:1].upper() + p[1:] if p else "" for p in parts)


def _create_icon(char: str, filename: str) -> None:
    font = {
        'A': [0b00111000, 0b01000100, 0b10000010, 0b10000010, 0b11111110, 0b10000010, 0b10000010, 0b00000000],
        'B': [0b11111100, 0b10000010, 0b10000010, 0b11111100, 0b10000010, 0b10000010, 0b11111100, 0b00000000],
        'C': [0b01111110, 0b10000000, 0b10000000, 0b10000000, 0b10000000, 0b10000000, 0b01111110, 0b00000000],
        'D': [0b11111100, 0b10000010, 0b10000010, 0b10000010, 0b10000010, 0b10000010, 0b11111100, 0b00000000],
        'E': [0b11111110, 0b10000000, 0b10000000, 0b11111100, 0b10000000, 0b10000000, 0b11111110, 0b00000000],
        'F': [0b11111110, 0b10000000, 0b10000000, 0b11111100, 0b10000000, 0b10000000, 0b10000000, 0b00000000],
        'G': [0b01111110, 0b10000000, 0b10000000, 0b10001110, 0b10000010, 0b10000010, 0b01111110, 0b00000000],
        'H': [0b10000010, 0b10000010, 0b10000010, 0b11111110, 0b10000010, 0b10000010, 0b10000010, 0b00000000],
        'I': [0b01111100, 0b00010000, 0b00010000, 0b00010000, 0b00010000, 0b00010000, 0b01111100, 0b00000000],
        'J': [0b00111110, 0b00000010, 0b00000010, 0b00000010, 0b10000010, 0b10000010, 0b01111100, 0b00000000],
        'K': [0b10000010, 0b10000100, 0b10001000, 0b10110000, 0b11001000, 0b10000100, 0b10000010, 0b00000000],
        'L': [0b10000000, 0b10000000, 0b10000000, 0b10000000, 0b10000000, 0b10000000, 0b11111110, 0b00000000],
        'M': [0b10000010, 0b11000110, 0b10101010, 0b10010010, 0b10000010, 0b10000010, 0b10000010, 0b00000000],
        'N': [0b10000010, 0b11000010, 0b10100010, 0b10010010, 0b10001010, 0b10000110, 0b10000010, 0b00000000],
        'O': [0b01111100, 0b10000010, 0b10000010, 0b10000010, 0b10000010, 0b10000010, 0b01111100, 0b00000000],
        'P': [0b11111100, 0b10000010, 0b10000010, 0b11111100, 0b10000000, 0b10000000, 0b10000000, 0b00000000],
        'Q': [0b01111100, 0b10000010, 0b10000010, 0b10000010, 0b10001010, 0b10000100, 0b01111010, 0b00000000],
        'R': [0b11111100, 0b10000010, 0b10000010, 0b11111100, 0b10001000, 0b10000100, 0b10000010, 0b00000000],
        'S': [0b01111100, 0b10000010, 0b10000000, 0b01111100, 0b00000010, 0b10000010, 0b01111100, 0b00000000],
        'T': [0b11111110, 0b00010000, 0b00010000, 0b00010000, 0b00010000, 0b00010000, 0b00010000, 0b00000000],
        'U': [0b10000010, 0b10000010, 0b10000010, 0b10000010, 0b10000010, 0b10000010, 0b01111100, 0b00000000],
        'V': [0b10000010, 0b10000010, 0b10000010, 0b01000100, 0b01000100, 0b00101000, 0b00010000, 0b00000000],
        'W': [0b10000010, 0b10000010, 0b10000010, 0b10010010, 0b10101010, 0b11000110, 0b10000010, 0b00000000],
        'X': [0b10000010, 0b01000100, 0b00101000, 0b00010000, 0b00101000, 0b01000100, 0b10000010, 0b00000000],
        'Y': [0b10000010, 0b01000100, 0b00101000, 0b00010000, 0b00010000, 0b00010000, 0b00010000, 0b00000000],
        'Z': [0b11111110, 0b00000010, 0b00000100, 0b00001000, 0b00010000, 0b00100000, 0b11111110, 0b00000000],
    }
    w = h = 512
    bg = (66, 135, 245)
    s = w // 16
    ox = (w - 8 * s) // 2
    oy = (h - 8 * s) // 2
    pix = bytearray()
    for y in range(h):
        for x in range(w):
            if char.upper() in font and ox <= x < ox + 8 * s and oy <= y < oy + 8 * s:
                row = font[char.upper()][(y - oy) // s]
                if row & (1 << (7 - (x - ox) // s)):
                    pix += b"\xff\xff\xff\xff"
                    continue
            pix += bytes([bg[0], bg[1], bg[2], 255])
    def chunk(t, d):
        return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    raw = b''.join(b'\x00' + pix[i*w*4:(i+1)*w*4] for i in range(h))
    data = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0))
    data += chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b'')
    Path(filename).write_bytes(data)


def cmd_setup(args: argparse.Namespace) -> None:
    """Initialise the template by replacing placeholder values."""
    base_package = input(f"Base package [{OLD_PACKAGE}]: ") or OLD_PACKAGE
    mod_id = input(f"Mod id [{OLD_MOD_ID}]: ") or OLD_MOD_ID
    mod_name = input(f"Mod name [{OLD_MOD_NAME}]: ") or OLD_MOD_NAME
    author = input(f"Author [{OLD_AUTHOR}]: ") or OLD_AUTHOR
    version = input(f"Initial version [{_default_version()}]: ") or _default_version()

    class_prefix = _to_camel(mod_name)
    icon_path = Path("common/src/main/resources/icon.png")

    replacements = {
        OLD_PACKAGE: base_package,
        OLD_MOD_ID: mod_id,
        OLD_MOD_NAME: mod_name,
        OLD_AUTHOR: author,
        "TemplateMod": f"{class_prefix}Mod",
        "TemplateFabric": f"{class_prefix}Fabric",
        "TemplateForge": f"{class_prefix}Forge",
        "TemplateNeoForge": f"{class_prefix}NeoForge",
    }

    print(
        "This will update package names, identifiers and the changelog in this project."
    )
    if not AUTO_YES and input("Proceed? [y/N] ").lower() != "y":
        print("Aborted")
        return

    print(f"{CYAN}Updating file contents...{RESET}")
    for path in Path('.').rglob('*'):
        if '.git' in path.parts:
            continue
        if path.is_file():
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            replaced = False
            for old, new in replacements.items():
                if old in text:
                    text = text.replace(old, new)
                    replaced = True
            if replaced:
                path.write_text(text, encoding="utf-8")
                print(f"{GREEN}Modified{RESET} {path}")

    print(f"{CYAN}Renaming package directories...{RESET}")
    old_parts = OLD_PACKAGE.split('.')
    new_parts = base_package.split('.')
    for module in ['common', 'fabric', 'forge', 'neoforge']:
        src = Path(module, 'src', 'main', 'java')
        old_dir = src.joinpath(*old_parts)
        if old_dir.exists():
            new_dir = src.joinpath(*new_parts)
            new_dir.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(old_dir), str(new_dir))
            print(f"{GREEN}Moved{RESET} {old_dir} -> {new_dir}")

    print(f"{CYAN}Renaming files...{RESET}")
    for path in Path('.').rglob('*'):
        if '.git' in path.parts:
            continue
        if path.is_file():
            new_name = path.name
            if OLD_MOD_ID in new_name:
                new_name = new_name.replace(OLD_MOD_ID, mod_id)
            if OLD_PACKAGE in new_name:
                new_name = new_name.replace(OLD_PACKAGE, base_package)
            if "Template" in new_name:
                new_name = new_name.replace("Template", class_prefix)
            if new_name != path.name:
                new_path = path.with_name(new_name)
                path.rename(new_path)
                print(f"{GREEN}Renamed{RESET} {path} -> {new_path}")

    props_path = Path("gradle.properties")
    text = props_path.read_text(encoding="utf-8")
    text = re.sub(r"(?m)^version=.*$", f"version={version}", text)
    props_path.write_text(text, encoding="utf-8")
    print(f"{GREEN}Set version to {version}{RESET}")

    chg_path = Path("changelog.md")
    chg_lines = chg_path.read_text(encoding="utf-8").splitlines()
    entry = [f"## {version}", "", "Initial Implementation", ""]
    try:
        def_idx = chg_lines.index("## 1.0.0")
        end_idx = def_idx + 1
        while end_idx < len(chg_lines) and not chg_lines[end_idx].startswith("## "):
            end_idx += 1
        del chg_lines[def_idx:end_idx]
    except ValueError:
        pass
    try:
        idx = chg_lines.index("## Types of changes")
    except ValueError:
        idx = len(chg_lines)
    chg_lines[idx:idx] = entry
    chg_path.write_text("\n".join(chg_lines) + "\n", encoding="utf-8")
    print(f"{GREEN}Updated changelog{RESET}")

    if not icon_path.exists():
        _create_icon(mod_name[0], icon_path)
        print(f"{GREEN}Created {icon_path}{RESET}")
    else:
        print(f"{CYAN}Skipped icon generation{RESET}")

    print(f"{GREEN}Template initialized.{RESET}")


# ---------------------------------------------------------------------------
# self-update functionality
# ---------------------------------------------------------------------------

def cmd_update(args: argparse.Namespace) -> None:
    """Download the latest version of Moddy and replace this file."""
    # Users should be aware that running the downloaded code could be risky.
    print("WARNING: this will download and execute code from the internet.")
    print(f"Source: {UPDATE_URL}")
    if not AUTO_YES and input("Are you sure you want to continue? [y/N] ").lower() != "y":
        print("Aborted")
        return
    try:
        new_code = _fetch_url_text(UPDATE_URL)
    except Exception as e:
        print(f"Failed to download update: {e}")
        return

    m = re.search(r"MODDY_VERSION\s*=\s*['\"]([^'\"]+)['\"]", new_code)
    new_version = m.group(1) if m else "unknown"
    if new_version == MODDY_VERSION:
        print("Moddy is already up to date.")
        return

    script_path = Path(__file__).resolve()
    backup = script_path.with_suffix(".bak")
    try:
        shutil.copy2(script_path, backup)
        script_path.write_text(new_code, encoding="utf-8")
    except Exception as e:
        print(f"Update failed: {e}")
        return
    print(f"Updated Moddy from {MODDY_VERSION} to {new_version}")
    print(f"A backup of the previous version was saved to {backup}")


# ---------------------------------------------------------------------------
# command line interface
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Moddy - helper for the multiloader template",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Assume yes for all confirmation prompts",
    )
    parser.add_argument("command", nargs="?", help="Command to run")
    parser.add_argument("args", nargs=argparse.REMAINDER)
    return parser


def main(argv=None) -> None:
    parser = build_parser()
    # Parse global options (-y) and the command name first
    ns, rest = parser.parse_known_args(argv or sys.argv[1:])
    global AUTO_YES
    AUTO_YES = ns.yes
    command = ns.command or "help"

    subparsers = {
        "add-service": cmd_add_service,
        "open-libs": cmd_open_libs,
        "set-minecraft-version": cmd_set_minecraft_version,
        "setup": cmd_setup,
        "update": cmd_update,
        "help": lambda a: parser.print_help(),
        "version": lambda a: print(MODDY_VERSION),
    }

    if command not in subparsers:
        parser.print_help()
        return

    func = subparsers[command]
    subparser = argparse.ArgumentParser(prog=f"{Path(sys.argv[0]).name} {command}")

    if func is cmd_add_service:
        subparser.add_argument("name", help="Service interface name")
    elif func is cmd_open_libs:
        subparser.add_argument("loader", choices=["fabric", "forge", "neoforge"], help="Loader to open the output for")
    elif func is cmd_set_minecraft_version:
        subparser.add_argument("version", help="Minecraft version, e.g. 1.21.5")

    args = subparser.parse_args(rest)
    func(args)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        sys.exit(1)

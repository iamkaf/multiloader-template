#!/usr/bin/env python3
"""Initialize the template by replacing placeholder values.

This script renames packages, class names and identifiers so that a freshly
cloned template is immediately ready for development. It prints colour coded
logs to help the user follow what is happening.
"""

import os
import re
import shutil
import struct
import zlib
from pathlib import Path

# Read the current template version from gradle.properties to use as default
def default_version() -> str:
    try:
        text = Path("gradle.properties").read_text(encoding="utf-8")
        m = re.search(r"^version=(.*)$", text, re.MULTILINE)
        if m:
            return m.group(1).strip()
    except Exception:
        pass
    return "1.0.0"

# Basic ANSI escape codes for coloured output
RESET = "\033[0m"
GREEN = "\033[32m"
CYAN = "\033[36m"

OLD_PACKAGE = "com.example.modtemplate"
OLD_MOD_ID = "examplemod"
OLD_MOD_NAME = "Example Mod"
OLD_AUTHOR = "yourname"

# Collect new values from the user with defaults.
base_package = input(f"Base package [{OLD_PACKAGE}]: ") or OLD_PACKAGE
mod_id = input(f"Mod id [{OLD_MOD_ID}]: ") or OLD_MOD_ID
mod_name = input(f"Mod name [{OLD_MOD_NAME}]: ") or OLD_MOD_NAME
author = input(f"Author [{OLD_AUTHOR}]: ") or OLD_AUTHOR
version = input(f"Initial version [{default_version()}]: ") or default_version()

def to_camel(value: str) -> str:
    """Convert snake_case or space separated names to CamelCase without losing existing capitals."""
    parts = re.split(r"[_\-\s]+", value)
    return "".join(p[:1].upper() + p[1:] if p else "" for p in parts)

# Class prefix derived from the mod id or name
class_prefix = to_camel(mod_name)

ICON_PATH = Path("common/src/main/resources/icon.png")

def create_icon(char: str, filename: str) -> None:
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

# Replace text in all files under the project.
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

# Rename package directories across modules.
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

# Rename files that contain the old mod id or old package in their name.
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

# Update version in gradle.properties
props_path = Path("gradle.properties")
text = props_path.read_text(encoding="utf-8")
text = re.sub(r"(?m)^version=.*$", f"version={version}", text)
props_path.write_text(text, encoding="utf-8")
print(f"{GREEN}Set version to {version}{RESET}")

# Insert an entry in changelog.md for the chosen version
chg_path = Path("changelog.md")
chg_lines = chg_path.read_text(encoding="utf-8").splitlines()
entry = [f"## {version}", "", "Initial Implementation", ""]

# Remove the template's default version entry if present
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

if not ICON_PATH.exists():
    create_icon(mod_name[0], ICON_PATH)
    print(f"{GREEN}Created {ICON_PATH}{RESET}")
else:
    print(f"{CYAN}Skipped icon generation{RESET}")

print(f"{GREEN}Template initialized.{RESET}")

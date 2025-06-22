#!/usr/bin/env python3
"""Create a platform service interface and implementations.

This helper script creates a new service interface under ``common`` and
implementations for all loaders.  A matching ``META-INF/services`` entry is
also written for each loader.  Run the script with the desired service name,
for example::

    python scripts/add_service.py IExampleService

The script shows the files it will create and asks for confirmation before
writing anything to disk.
"""
import argparse
import re
import sys
from pathlib import Path

def parse_group(props_path: Path) -> str:
    text = props_path.read_text(encoding="utf-8")
    m = re.search(r"^group=(.+)$", text, re.MULTILINE)
    if not m:
        raise RuntimeError("Could not determine group property")
    return m.group(1).strip()

def main(argv=None):
    parser = argparse.ArgumentParser(description="Create service skeleton")
    parser.add_argument("name", help="Service interface name, e.g. IExampleService")
    args = parser.parse_args(argv)

    name = args.name.strip()
    if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name):
        parser.error("Illegal characters in service name")

    group = parse_group(Path("gradle.properties"))
    pkg_path = group.replace(".", "/")
    service_fqn = f"{group}.platform.services.{name}"

    interface_path = Path("common/src/main/java") / pkg_path / "platform" / "services" / f"{name}.java"
    fabric_impl_path = Path("fabric/src/main/java") / pkg_path / "platform" / f"Fabric{name}.java"
    forge_impl_path = Path("forge/src/main/java") / pkg_path / "platform" / f"Forge{name}.java"
    neo_impl_path = Path("neoforge/src/main/java") / pkg_path / "platform" / f"NeoForge{name}.java"

    fabric_meta = Path("fabric/src/main/resources/META-INF/services") / service_fqn
    forge_meta = Path("forge/src/main/resources/META-INF/services") / service_fqn
    neo_meta = Path("neoforge/src/main/resources/META-INF/services") / service_fqn

    files = {
        interface_path: f"package {group}.platform.services;\n\npublic interface {name} {{\n}}\n",
        fabric_impl_path: f"package {group}.platform;\n\nimport {service_fqn};\n\npublic class Fabric{name} implements {name} {{\n}}\n",
        forge_impl_path: f"package {group}.platform;\n\nimport {service_fqn};\n\npublic class Forge{name} implements {name} {{\n}}\n",
        neo_impl_path: f"package {group}.platform;\n\nimport {service_fqn};\n\npublic class NeoForge{name} implements {name} {{\n}}\n",
        fabric_meta: f"{group}.platform.Fabric{name}\n",
        forge_meta: f"{group}.platform.Forge{name}\n",
        neo_meta: f"{group}.platform.NeoForge{name}\n",
    }

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

    if input("Proceed? [y/N] ").lower() != "y":
        print("Aborted")
        return

    for path, content in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"Created {path}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()  # newline after Ctrl+C
        sys.exit(1)

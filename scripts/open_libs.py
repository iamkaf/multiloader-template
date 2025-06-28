#!/usr/bin/env python3
"""Open the build/libs folder for a loader in the system file explorer."""

import argparse
import os
import platform
import subprocess
from pathlib import Path


def open_dir(path: Path) -> None:
    """Open *path* in Explorer, Finder or the default file manager."""
    system = platform.system()
    if system == "Windows":
        os.startfile(path)  # type: ignore[attr-defined]
    elif system == "Darwin":
        subprocess.run(["open", str(path)], check=False)
    else:
        subprocess.run(["xdg-open", str(path)], check=False)


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(
        description="Open the build/libs folder for the given loader"
    )
    parser.add_argument(
        "loader",
        choices=["fabric", "forge", "neoforge"],
        help="Loader to open the output for",
    )
    args = parser.parse_args(argv)
    libs = Path(args.loader) / "build" / "libs"
    if not libs.is_dir():
        print(f"No libs folder found at {libs}. Run a build first.")
        return
    open_dir(libs)


if __name__ == "__main__":
    main()

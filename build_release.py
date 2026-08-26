"""Build an uploadable QGIS plugin archive after strict release validation."""

from __future__ import annotations

import configparser
import sys
import zipfile
from pathlib import Path

from validate_release import PLUGIN, ROOT, validate


EXCLUDED_PARTS = {"__pycache__", ".pytest_cache"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


def archive_name() -> str:
    parser = configparser.ConfigParser(interpolation=None)
    parser.read(PLUGIN / "metadata.txt", encoding="utf-8")
    version = parser["general"]["version"].strip()
    return f"{PLUGIN.name}-{version}.zip"


def should_include(path: Path) -> bool:
    relative = path.relative_to(PLUGIN)
    return not any(part in EXCLUDED_PARTS for part in relative.parts) and (
        path.suffix.lower() not in EXCLUDED_SUFFIXES
    )


def main() -> int:
    errors, warnings = validate(technical=False)
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(
            "Refusing to build an upload archive until all release "
            "blockers are fixed."
        )
        return 1

    destination_dir = ROOT / "dist"
    destination_dir.mkdir(exist_ok=True)
    destination = destination_dir / archive_name()
    with zipfile.ZipFile(
        destination, "w", compression=zipfile.ZIP_DEFLATED
    ) as archive:
        for path in sorted(PLUGIN.rglob("*")):
            if path.is_file() and should_include(path):
                archive.write(
                    path, Path(PLUGIN.name) / path.relative_to(PLUGIN)
                )

    print(f"Built: {destination}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

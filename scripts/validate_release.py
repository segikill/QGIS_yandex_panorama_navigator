"""Validate a QGIS plugin source tree before packaging or upload."""

from __future__ import annotations

import argparse
import configparser
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "yandex_panorama_navigator"
METADATA = PLUGIN / "metadata.txt"

REQUIRED_METADATA = (
    "name",
    "qgisMinimumVersion",
    "description",
    "about",
    "version",
    "author",
    "email",
    "repository",
)
PLACEHOLDER_PREFIX = "REPLACE_WITH_"
ASCII_FOLDER = re.compile(r"^[A-Za-z_-][A-Za-z0-9_-]*$")
EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
INTERNAL_RENDERER = "core-stv-renderer.maps.yandex.net"


def is_http_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def validate(*, technical: bool = False) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if not ASCII_FOLDER.fullmatch(PLUGIN.name):
        errors.append(
            "Plugin root folder must contain only supported ASCII characters."
        )

    for required_file in (
        "metadata.txt",
        "__init__.py",
        "LICENSE",
        "README.md",
    ):
        if not (PLUGIN / required_file).is_file():
            errors.append(f"Missing required file: {required_file}")

    parser = configparser.ConfigParser(interpolation=None)
    parser.optionxform = str
    try:
        with METADATA.open("r", encoding="utf-8") as metadata_file:
            parser.read_file(metadata_file)
    except (OSError, UnicodeError, configparser.Error) as error:
        errors.append(f"Cannot parse UTF-8 metadata.txt: {error}")
        return errors, warnings

    if not parser.has_section("general"):
        errors.append("metadata.txt has no [general] section.")
        return errors, warnings

    metadata = parser["general"]
    for field in REQUIRED_METADATA:
        if not metadata.get(field, "").strip():
            errors.append(f"Required metadata field is empty: {field}")

    release_blockers = []
    for field in ("author", "email", "repository", "tracker", "homepage"):
        if metadata.get(field, "").strip().startswith(PLACEHOLDER_PREFIX):
            release_blockers.append(
                f"Replace placeholder metadata field: {field}"
            )

    email = metadata.get("email", "").strip()
    if (
        email
        and not email.startswith(PLACEHOLDER_PREFIX)
        and not EMAIL.fullmatch(email)
    ):
        errors.append("Metadata email is not syntactically valid.")

    for field in ("repository", "tracker", "homepage"):
        value = metadata.get(field, "").strip()
        if (
            value
            and not value.startswith(PLACEHOLDER_PREFIX)
            and not is_http_url(value)
        ):
            errors.append(f"Metadata {field} must be an HTTP(S) URL.")

    if "supportsQt6" in metadata:
        errors.append(
            "Remove obsolete supportsQt6 metadata; use "
            "qgisMaximumVersion instead."
        )

    icon_value = metadata.get("icon", "").strip()
    icon = PLUGIN / icon_value
    if not icon.is_file():
        errors.append(f"Metadata icon does not exist: {icon_value}")
    elif icon.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
        errors.append(
            "Official QGIS metadata should reference a PNG or JPEG icon."
        )

    license_file = PLUGIN / "LICENSE"
    if license_file.is_file() and license_file.stat().st_size < 15_000:
        errors.append("LICENSE does not contain the complete GPL v2 text.")

    unwanted = []
    for path in PLUGIN.rglob("*"):
        if path.is_dir() and path.name == "__pycache__":
            unwanted.append(path)
        elif path.is_file() and path.suffix.lower() in {".pyc", ".pyo"}:
            unwanted.append(path)
    if unwanted:
        errors.append(
            "Generated Python files are present in the plugin source."
        )

    uses_internal_renderer = any(
        INTERNAL_RENDERER in path.read_text(encoding="utf-8", errors="ignore")
        for path in PLUGIN.rglob("*.py")
    )
    authorization = ROOT / "YANDEX_AUTHORIZATION.md"
    if uses_internal_renderer and not authorization.is_file():
        release_blockers.append(
            "Undocumented Yandex renderer is enabled but "
            "YANDEX_AUTHORIZATION.md is absent."
        )

    if technical:
        warnings.extend(release_blockers)
    else:
        errors.extend(release_blockers)
    return errors, warnings


def main() -> int:
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument(
        "--technical",
        action="store_true",
        help=(
            "Treat owner/legal release blockers as warnings while checking "
            "structure."
        ),
    )
    arguments = argument_parser.parse_args()
    errors, warnings = validate(technical=arguments.technical)

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")

    if errors:
        print(
            "Release validation failed: "
            f"{len(errors)} error(s), {len(warnings)} warning(s)."
        )
        return 1
    print(f"Release validation passed with {len(warnings)} warning(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

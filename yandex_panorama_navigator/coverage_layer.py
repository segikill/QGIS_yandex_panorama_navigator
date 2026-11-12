"""Helpers for the experimental Yandex panorama coverage raster layer."""

from __future__ import annotations

import re
from typing import Optional


COVERAGE_LAYER_NAME = "Яндекс Панорамы — покрытие"
COVERAGE_PROPERTY = "yandex_panorama_navigator/coverage"
COVERAGE_VERSION_PROPERTY = "yandex_panorama_navigator/coverage_version"
FALLBACK_VERSION = "2026.08.25.23.14-1_26.08.24-2-30759"

_VERSION_PATTERN = re.compile(
    rb"20\d{2}\.\d{2}\.\d{2}\.\d{2}\.\d{2}-\d+_\d{2}\.\d{2}\.\d{2}-\d+-\d+"
)


def extract_coverage_version(data: bytes) -> Optional[str]:
    """Extract the street-view renderer version from Yandex Maps HTML."""
    match = _VERSION_PATTERN.search(data)
    return match.group(0).decode("ascii") if match else None


def is_valid_coverage_version(version: object) -> bool:
    if not isinstance(version, str):
        return False
    return (
        _VERSION_PATTERN.fullmatch(version.encode("ascii", errors="ignore"))
        is not None
    )


def build_coverage_gdal_wms(version: str) -> str:
    """Build an inline GDAL TMS definition using Yandex's ellipsoidal grid."""
    if not is_valid_coverage_version(version):
        raise ValueError("Invalid Yandex panorama coverage version")

    return f"""<GDAL_WMS>
  <Service name="TMS">
    <ServerUrl>https://core-stv-renderer.maps.yandex.net/2.x/tiles?l=stv&amp;x=${{x}}&amp;y=${{y}}&amp;z=${{z}}&amp;scale=1&amp;v={version}</ServerUrl>
  </Service>
  <DataWindow>
    <UpperLeftX>-20037508.342789244</UpperLeftX>
    <UpperLeftY>20037508.342789244</UpperLeftY>
    <LowerRightX>20037508.342789244</LowerRightX>
    <LowerRightY>-20037508.342789244</LowerRightY>
    <TileLevel>19</TileLevel>
    <TileCountX>1</TileCountX>
    <TileCountY>1</TileCountY>
    <YOrigin>top</YOrigin>
  </DataWindow>
  <Projection>EPSG:3395</Projection>
  <BlockSizeX>256</BlockSizeX>
  <BlockSizeY>256</BlockSizeY>
  <BandsCount>4</BandsCount>
  <DataType>Byte</DataType>
</GDAL_WMS>"""

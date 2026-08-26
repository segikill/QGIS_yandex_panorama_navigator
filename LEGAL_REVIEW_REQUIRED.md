# Publication blocker: Yandex service terms

This source tree is a technical release candidate, not an approved upload package.

The coverage implementation requests an undocumented Yandex renderer endpoint and displays the returned coverage over third-party cartographic materials in QGIS. The Yandex Maps terms published on 13 May 2026 state that API services require an API key and prohibit panorama display in third-party services or on third-party cartographic materials.

Before publishing this functionality, obtain one of the following:

1. Written permission or an appropriate agreement from Yandex covering the coverage renderer and its display in QGIS; or
2. A documented, licensed Yandex API product that explicitly permits this exact use.

If permission is not available, produce a separate public edition that removes `coverage_layer.py`, all requests to `core-stv-renderer.maps.yandex.net`, and the temporary coverage overlay. The click/drag tool may continue to open the public Yandex Maps website, subject to a separate terms review.

Relevant terms: https://yandex.ru/legal/maps_api/ru

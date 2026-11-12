# Yandex Panorama Coverage Overlay for QGIS

Experimental QGIS plugin that temporarily displays Yandex panorama coverage above the map canvas and opens Yandex Maps in the system browser at a selected position and viewing direction.

The coverage is a private canvas-only overlay. It is never registered in `QgsProject`, never appears in the Layers panel and is not saved in `.qgz` projects. The overlay is removed after a panorama opens or selection is cancelled.

## Repository layout

- `yandex_panorama_navigator/` — installable QGIS plugin source.
- `tests/` — dependency-free and QGIS-runtime regression tests.
- `scripts/` — validation and release packaging tools.
- `.github/workflows/checks.yml` — static analysis and unit-test workflow.

## Compatibility

- Declared: QGIS 3.28–3.99.
- Tested: QGIS 3.28.1, 3.34.3 and 3.44.8 on Windows.
- QGIS 4 is not declared because the plugin has not been tested in a complete QGIS 4 Python runtime.

## Development checks

```powershell
python scripts/validate_release.py --technical
python -B -m unittest discover -s tests -p "test_*.py"
```

The installable archive must contain one top-level directory named `yandex_panorama_navigator`. Development files, tests and caches must not be included in the plugin ZIP.

## Important publication notice

The coverage implementation currently uses an undocumented Yandex renderer endpoint. This project is not affiliated with or endorsed by Yandex. Before public distribution, the publisher must confirm that the intended use is permitted by the current Yandex terms or obtain written permission from Yandex. See `LEGAL_REVIEW_REQUIRED.md`.

## License

GNU General Public License version 2 or, at your option, any later version. See `LICENSE`.

---

# Русское описание

Плагин временно показывает покрытие Яндекс Панорам поверх холста QGIS. Слой существует только внутри холста, не попадает в список слоёв и проект QGIS. После выбора точки панорама открывается во внешнем браузере, а покрытие удаляется.

Исходники устанавливаемого плагина находятся в каталоге `yandex_panorama_navigator/`.

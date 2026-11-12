# Yandex Panorama Coverage Overlay

Experimental QGIS plugin that temporarily displays Yandex panorama coverage above the map canvas and opens Yandex Maps at a selected position and viewing direction.

## Important publication notice

This technical release candidate uses an undocumented Yandex coverage renderer. It is not affiliated with or endorsed by Yandex. Do not upload or distribute the coverage-enabled build until the publisher has confirmed that the intended use is permitted by the current Yandex terms or has obtained written permission from Yandex.

## Features

- Displays coverage only in the map canvas, above all project layers.
- Does not register the coverage in `QgsProject`, the Layers panel or saved `.qgz` projects.
- Removes the coverage after opening a panorama or pressing `Esc`.
- Converts coordinates from the project CRS to EPSG:4326.
- Opens Yandex Maps only in the default external browser, without extra Python dependencies.
- Allows dragging from the selected point to define the initial viewing azimuth.

Unlike the existing deprecated **Yandex Panoramas** plugin in the official QGIS repository, this plugin adds temporary coverage visualization and drag-to-set direction while keeping the project layer list unchanged.

## Installation for testing

1. Keep the plugin ZIP compressed.
2. Open **Plugins → Manage and Install Plugins → Install from ZIP** in QGIS.
3. Select the release-candidate archive.
4. Enable experimental plugins if required.

## Usage

1. Click the panorama-coverage button on the plugin toolbar.
2. Wait for the blue coverage to appear above the current map.
3. Click a covered location, or drag to define the initial direction.
4. Yandex Maps opens in the default browser and the temporary coverage disappears.

The interface is currently Russian. English localization is recommended before a stable public release.

## Compatibility

- Declared: QGIS 3.28–3.99.
- Tested locally: QGIS 3.28, 3.34 and 3.44 on Windows.
- QGIS 4 is not declared in this release candidate because it has not been tested in an actual Qt6 QGIS runtime.

## Known limitations

- Coverage depends on an undocumented renderer and may stop working without notice.
- Automatic renderer-version discovery depends on the current Yandex Maps page structure.
- If no panorama exists near a selected point, Yandex Maps may open its ordinary map view.

## License

GNU General Public License version 2 or, at the user's option, any later version. See `LICENSE`.

---

# Русская инструкция

Плагин временно показывает покрытие Яндекс Панорам поверх холста QGIS и открывает панораму по выбранной точке.

Покрытие не добавляется в проект, список слоёв или файл `.qgz`. После открытия панорамы либо отмены клавишей `Esc` оно удаляется с холста.

Панорама открывается только во внешнем браузере. В плагине нет `PyQtWebEngine`, встроенной браузерной панели и команды установки дополнительных PyQt-пакетов.

Сборка с покрытием использует недокументированный адрес Яндекса и не должна публиковаться до подтверждения правомерности такого использования или получения письменного разрешения Яндекса.

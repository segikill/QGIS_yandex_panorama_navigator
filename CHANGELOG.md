# Changelog

All notable changes follow semantic versioning.

## [1.2.0] - 2026-08-26

### Added

- Temporary Yandex panorama coverage rendered above the QGIS canvas.
- Automatic discovery and local caching of the coverage renderer version.
- Click selection and drag-to-set viewing direction.

### Changed

- Coverage is no longer registered in `QgsProject` or shown in the Layers panel.
- Coverage is removed after opening a panorama or canceling selection.
- Removed the embedded browser mode, QtWebEngine detection and pip-install guidance.

### Security

- The plugin no longer loads any QtWebEngine native library or suggests modifying the QGIS Python environment.

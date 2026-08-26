# QGIS Plugins Repository release checklist

## Blocking before upload

- [x] Replace all `REPLACE_WITH_...` values in `metadata.txt` with real data.
- [ ] Publish the source in the public repository; it currently exists but is empty.
- [x] Use the distinct final name `Yandex Panorama Coverage Overlay`.
- [ ] Obtain written Yandex permission or remove the coverage renderer as described in `LEGAL_REVIEW_REQUIRED.md`.
- [x] Keep the supported range at `3.28–3.99`; an actual QGIS 4 Python runtime was not available for testing.
- [ ] Create an OSGeo account capable of uploading to plugins.qgis.org.

## Technical checks

- [ ] Run `python scripts/validate_release.py`.
- [ ] Run helper tests with the system Python.
- [ ] Load, enable, use and unload the plugin in a clean QGIS profile.
- [x] Test QGIS 3.28.1, 3.34.3 and 3.44.8 using runtime and real-canvas checks.
- [ ] If advertising QGIS 4 support, run the official pyqgis4-checker and test an actual QGIS 4 release.
- [ ] Confirm the ZIP has one ASCII root directory named `yandex_panorama_navigator`.
- [ ] Confirm `metadata.txt`, `__init__.py`, `LICENSE`, `README.md` and the PNG icon are included.
- [ ] Confirm the archive contains no `.pyc`, `__pycache__`, tests, credentials or development files.

## Upload

- [ ] Tag the source repository with the exact final version.
- [ ] Build the archive with `qgis-plugin-ci package <version>` or the validated packaging script.
- [ ] Upload at https://plugins.qgis.org/ and wait for staff approval.
- [ ] Review automated security and Qt6 reports on the uploaded version page.

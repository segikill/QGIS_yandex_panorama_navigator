# Yandex Panorama Coverage Overlay — release workspace

This repository layout is prepared for the QGIS Plugins Repository, but publication is blocked until the mandatory owner metadata and Yandex service authorization are resolved.

The installable plugin source is in `yandex_panorama_navigator/`.

Before creating a public release, read:

- `LEGAL_REVIEW_REQUIRED.md`
- `RELEASE_CHECKLIST.md`
- `CHANGELOG.md`

Run the local release audit:

```powershell
python scripts/validate_release.py
```

The owner metadata is complete. The strict audit is expected to fail while the undocumented coverage renderer remains enabled without recorded authorization.

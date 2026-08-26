# Публикация исходников 1.2.0 в GitHub

Репозиторий `https://github.com/segikill/QGIS_yandex_panorama_navigator` создан и публично доступен, но на 26 августа 2026 года остаётся пустым.

Загрузите в корень репозитория всё содержимое release workspace, включая скрытые файлы `.gitignore`, `.qgis-plugin-ci` и каталог `.github`. Каталог `yandex_panorama_navigator` должен находиться непосредственно в корне репозитория.

Пример через Git:

```powershell
git clone https://github.com/segikill/QGIS_yandex_panorama_navigator.git
cd QGIS_yandex_panorama_navigator
# Скопируйте сюда содержимое release workspace.
git add .
git commit -m "Release 1.2.0"
git tag 1.2.0
git push origin main
git push origin 1.2.0
```

После публикации убедитесь, что GitHub показывает `README.md`, `CHANGELOG.md`, `LICENSE`, каталог плагина и исходные `.py`-файлы. Содержимое репозитория должно совпадать с исходниками в публикационном ZIP; не добавляйте `__pycache__`, `.pyc`, локальные виртуальные окружения и ключи доступа.

Публикационный ZIP нельзя создавать до документирования разрешения Яндекса на используемый сценарий покрытия.

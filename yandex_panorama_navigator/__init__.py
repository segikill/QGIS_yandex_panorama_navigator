"""Yandex Panorama Navigator QGIS plugin entry point."""


def classFactory(iface):
    """Create the plugin instance for QGIS."""
    from .plugin import YandexPanoramaNavigatorPlugin

    return YandexPanoramaNavigatorPlugin(iface)

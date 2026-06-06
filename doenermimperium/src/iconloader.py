# DÖNERIMPERIUM™ - Icon Loader
# ==============================
import pygame
import os

# Pfad zur Ico-Datei (liegt in assets/)
_SRC_DIR  = os.path.dirname(os.path.abspath(__file__))
_BASE_DIR = os.path.dirname(_SRC_DIR)          # project root
_ICON_PATH = os.path.join(_BASE_DIR, "assets", "Döner.ico")


def load_icon() -> pygame.Surface | None:
    """Lädt Döner.ico und gibt eine pygame.Surface zurück.
    Gibt None zurück wenn die Datei nicht gefunden wird."""
    if not os.path.isfile(_ICON_PATH):
        print(f"[IconLoader] ⚠ Icon nicht gefunden: {_ICON_PATH}")
        return None
    try:
        icon = pygame.image.load(_ICON_PATH)
        print(f"[IconLoader] ✓ Icon geladen: {_ICON_PATH}")
        return icon
    except pygame.error as e:
        print(f"[IconLoader] ✗ Fehler beim Laden: {e}")
        return None


def set_window_icon() -> None:
    """Setzt das Fenster-Icon auf Döner.ico (muss vor pygame.display.set_mode aufgerufen werden)."""
    icon = load_icon()
    if icon:
        pygame.display.set_icon(icon)
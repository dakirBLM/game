"""
Thin wrapper around pygame._freetype that provides the same .render()
interface as pygame.font.Font, working around the circular-import bug
on Python 3.14 + pygame 2.6.
"""
import pygame

_ft_module = None

def _ensure_ft():
    global _ft_module
    if _ft_module is None:
        from pygame import _freetype
        _freetype.init()
        _ft_module = _freetype


class GameFont:
    """Drop-in replacement for a subset of pygame.font.Font."""

    def __init__(self, path, size):
        _ensure_ft()
        self._font = _ft_module.Font(path, size)
        self._size = size

    def render(self, text, antialias, color, background=None):
        """Return a Surface with the rendered text (ignores *antialias*)."""
        surf, rect = self._font.render(text, color)
        return surf

    def get_height(self):
        return self._font.get_sized_height(self._size)

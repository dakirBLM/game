import pygame
from Config import *
try:
    from image_helper import load_image
except Exception:
    import os, sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from image_helper import load_image


class SpriteSheet():

    def __init__(self, spriteSheetPath, spritePositions, tint=None):
        image = load_image(spriteSheetPath, use_alpha=True)
        self.sprites = []
        self.spritesFlipped = []
        for position in spritePositions:
            sprite = image.subsurface(pygame.Rect(position)).copy()
            if tint:
                sprite = SpriteSheet._apply_tint(sprite, tint)
            self.sprites.append(sprite)
            sprite = pygame.transform.flip(sprite, True, False)
            self.spritesFlipped.append(sprite)

    @staticmethod
    def _apply_tint(surface, tint_color):
        """Warm-tint a sprite: blend light/white pixels toward the tint color
        while keeping darker pixels (outlines, shadows) untouched."""
        tr, tg, tb = tint_color[:3]
        w, h = surface.get_size()
        tinted = surface.copy()
        try:
            pa = pygame.PixelArray(tinted)
            for y in range(h):
                for x in range(w):
                    color = tinted.unmap_rgb(pa[x][y])
                    r, g, b, a = color.r, color.g, color.b, color.a
                    if a == 0:
                        continue
                    # Lightness: how "white" the pixel is (0-1 scale)
                    lightness = min(r, g, b) / 255.0
                    # Only tint pixels that are grayish/white (lightness > 0.35)
                    if lightness > 0.35:
                        strength = min(1.0, (lightness - 0.35) / 0.55)
                        nr = int(r + (tr - r) * strength * 0.7)
                        ng = int(g + (tg - g) * strength * 0.7)
                        nb = int(b + (tb - b) * strength * 0.7)
                        nr = max(0, min(255, nr))
                        ng = max(0, min(255, ng))
                        nb = max(0, min(255, nb))
                        pa[x][y] = tinted.map_rgb((nr, ng, nb, a))
            pa.close()
        except Exception:
            # Fallback: use a simple multiply blend
            tint_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            tint_surf.fill((*tint_color[:3], 60))
            tinted.blit(tint_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return tinted


    def getSprites(self, flipped):
        if flipped == True:
            return self.spritesFlipped
        else:
            return self.sprites

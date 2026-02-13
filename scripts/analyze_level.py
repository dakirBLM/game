"""Analyze the TMX level layout."""
from pytmx.util_pygame import load_pygame
import pygame
pygame.init()
pygame.display.set_mode((1,1))
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'MagicForest', '04_LevelLoading'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'MagicForest'))
from Config import *
from image_helper import load_image
_orig = pygame.image.load
pygame.image.load = lambda p: load_image(p, use_alpha=True)
ld = load_pygame(LEVELS_PATH + 'Level1/level.tmx')
pygame.image.load = _orig

layer = ld.get_layer_by_name('Platforms')
tiles = [(x, y) for x, y, s in layer.tiles()]
print('Total platform tiles:', len(tiles))
rows = {}
for gx, gy in tiles:
    rows.setdefault(gy, []).append(gx)
for gy in sorted(rows.keys()):
    xs = sorted(rows[gy])
    gaps = []
    for i in range(len(xs)-1):
        diff = xs[i+1] - xs[i] - 1
        if diff > 0:
            gaps.append((xs[i], xs[i+1], diff))
    print('Row y=%d (px %d): x=[%d..%d] tiles=%d gaps=%s' % (gy, gy*16, xs[0], xs[-1], len(xs), gaps))

print()
for obj in ld.objects:
    n = getattr(obj, 'name', '')
    print('Object: name=%s x=%d y=%d w=%d h=%d' % (n, obj.x, obj.y, obj.width, obj.height))

print()
for lyr in ld.layers:
    lname = getattr(lyr, 'name', '?')
    ltype = type(lyr).__name__
    print('Layer: %s (%s)' % (lname, ltype))

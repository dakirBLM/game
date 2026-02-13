"""Debug hero pixel colors."""
import pygame
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'MagicForest', '04_LevelLoading'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'MagicForest'))
pygame.init()
screen = pygame.display.set_mode((960, 540))

from Config import *
from ClassLevel import Level

level = Level(screen)

# Run a few frames
for i in range(10):
    level.run()
    pygame.display.flip()

hero = level.hero.sprite
print('Hero state:', hero.currentState)
print('Hero rect:', hero.rect)
print('Hero image size:', hero.image.get_size())

img = hero.image
w, h = img.get_size()
print('--- non-transparent pixels in hero image ---')
count = 0
for y in range(0, h, 5):
    for x in range(0, w, 5):
        px = img.get_at((x, y))
        if px[3] > 0:
            print('  (%d,%d): RGBA=(%d,%d,%d,%d)' % (x, y, px[0], px[1], px[2], px[3]))
            count += 1
print('Total non-transparent sampled:', count)

# Check what the spritesheet looks like
ss = hero.spriteSheets['IDLE']
sprites = ss.getSprites(flipped=False)
print('\n--- IDLE sprites[0] pixels ---')
s0 = sprites[0]
for y in range(0, s0.get_height(), 10):
    for x in range(0, s0.get_width(), 10):
        px = s0.get_at((x, y))
        if px[3] > 0:
            print('  (%d,%d): RGBA=(%d,%d,%d,%d)' % (x, y, px[0], px[1], px[2], px[3]))

pygame.quit()

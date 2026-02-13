"""Quick hero pixel check."""
import pygame, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'MagicForest', '04_LevelLoading'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'MagicForest'))
os.environ['SDL_VIDEODRIVER'] = 'dummy'
pygame.init()
screen = pygame.display.set_mode((960, 540))

from Config import *
from ClassSpriteSheet import SpriteSheet

idleSprites = [
    (12, 12, 44, 52),
    (76, 12, 44, 52),
    (140, 12, 44, 52),
    (204, 12, 44, 52)
]

_tint = (160, 110, 60)
ss = SpriteSheet(SPRITESHEET_PATH + "Character/Idle/Idle-Sheet.png", idleSprites, tint=_tint)
sprites = ss.getSprites(flipped=False)
s0 = sprites[0]
print('Sprite 0 size:', s0.get_size())
for y in range(0, s0.get_height(), 10):
    for x in range(0, s0.get_width(), 10):
        px = s0.get_at((x, y))
        if px[3] > 0:
            print('  (%d,%d): R=%d G=%d B=%d A=%d' % (x, y, px[0], px[1], px[2], px[3]))
print('DONE')
pygame.quit()

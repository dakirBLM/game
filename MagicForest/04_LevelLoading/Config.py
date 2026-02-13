import os

# Assets: compute absolute path relative to the project root so loading works
# regardless of the current working directory.
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SPRITESHEET_PATH = os.path.join(BASE_DIR, 'Assets', 'SpriteSheets', 'Legacy-Fantasy - High Forest 2.3') + os.sep
LEVELS_PATH = os.path.join(BASE_DIR, 'MagicForest', 'Levels') + os.sep


# Window settings
WINDOW_WIDTH, WINDOW_HEIGHT = 960, 540

TILESIZE = 16

GRAVITY = 0.6

SPEED_HERO = 4
ANIMSPEED_HERO_DEFAULT = 0.25
ANIMSPEED_HERO_IDLE = 0.1

SPEED_BEE = 2
ANIMSPEED_BEE = 0.2
ANIMSPEED_BEE_ATTACK = 0.5

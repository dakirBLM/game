import pygame
import os
import subprocess
from pytmx.util_pygame import load_pygame
try:
    from image_helper import load_image
except Exception:
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from image_helper import load_image
import pygame as _pygame
from Config import *
from ClassHero import Hero
from ClassBee import Bee
from ClassTile import Tile
from ClassBackground import Background


# Stepping-stone platforms to connect isolated platform groups
# Each entry: (grid_x, grid_y, width_in_tiles)
BRIDGE_PLATFORMS = [
    (76, 27, 5),    # bridge row 28 (x=63-70) to row 27 (x=85-119)
    (96, 23, 5),    # step up from row 27 area
    (100, 20, 5),   # step toward row 17/18 area
    (80, 17, 5),    # bridge large gap in row 17
    (88, 17, 5),    # bridge large gap in row 17 (continued)
    (44, 19, 5),    # step from row 21 going left
    (37, 18, 5),    # step going left / up
    (28, 16, 5),    # step toward row 14
    (20, 15, 5),    # final step to row 14
    (95, 13, 5),    # step from row 15 up to row 11 area
    (84, 9, 5),     # step from row 11 to row 6
    (37, 6, 5),     # bridge first gap in row 5
    (56, 6, 5),     # bridge second gap in row 5
]


class Level:
    def __init__(self, displaySurface):
        self.displaySurface = displaySurface

        # Load TMX level (monkeypatch pygame.image.load for Pillow fallback)
        _orig_load = _pygame.image.load
        try:
            _pygame.image.load = lambda path: load_image(path, use_alpha=True)
            self.levelData = load_pygame(LEVELS_PATH + "Level1/level.tmx")
        finally:
            _pygame.image.load = _orig_load

        # Level dimensions from TMX
        self.level_pixel_width = self.levelData.width * self.levelData.tilewidth
        self.level_pixel_height = self.levelData.height * self.levelData.tileheight

        # Camera
        self.camera_x = 0.0

        # Audio
        self._init_audio()

        # Background
        self.background = Background()

        # Sprite groups
        self.hero = pygame.sprite.GroupSingle()
        self.mobs = pygame.sprite.Group()
        self.bees = pygame.sprite.Group()
        self.platformTiles = pygame.sprite.Group()

        # Load platform tiles from TMX
        layer = self.levelData.get_layer_by_name('Platforms')
        for x, y, tileSurface in layer.tiles():
            tile = Tile((x * TILESIZE, y * TILESIZE), tileSurface)
            self.platformTiles.add(tile)

        # Bridge single-tile gaps
        self._bridge_single_gaps()

        # Add designer bridge / stepping-stone platforms
        self._add_bridge_platforms()

        # Collect background tile layers
        self._collect_background_layers()

        # Spawn hero and mobs from TMX objects
        self._spawn_entities()


    # ─── Audio ────────────────────────────────────────────────────

    def _init_audio(self):
        music_file = os.path.join(BASE_DIR, 'Assets', 'Sound', 'Music',
                                  'Alexander Ehlers', 'Alexander Ehlers - Warped.mp3')
        sfx_file = os.path.join(BASE_DIR, 'Assets', 'Sound', 'SoundFX',
                                'KronBits', 'Retro Jump Classic 08.wav')

        self._use_afplay = False
        self.music_loaded = False
        self.jump_sfx = None
        self.jump_sfx_path = None
        self._afplay_proc = None

        try:
            if not hasattr(pygame, 'mixer'):
                self._use_afplay = True
            else:
                try:
                    if not pygame.mixer.get_init():
                        pygame.mixer.init()
                except Exception:
                    self._use_afplay = True

            if not self._use_afplay:
                if os.path.exists(music_file):
                    try:
                        pygame.mixer.music.load(music_file)
                        pygame.mixer.music.set_volume(0.6)
                        pygame.mixer.music.play(-1)
                        self.music_loaded = True
                    except Exception:
                        pass
                if os.path.exists(sfx_file):
                    try:
                        self.jump_sfx = pygame.mixer.Sound(sfx_file)
                    except Exception:
                        self.jump_sfx = None
            else:
                if os.path.exists(music_file):
                    try:
                        self._afplay_proc = subprocess.Popen(['afplay', music_file])
                        self.music_loaded = True
                    except Exception:
                        pass
                if os.path.exists(sfx_file):
                    self.jump_sfx_path = sfx_file
        except Exception:
            self.jump_sfx = None

    def stop_audio(self):
        try:
            if not self._use_afplay:
                try:
                    if getattr(pygame, 'mixer', None) and pygame.mixer.get_init():
                        pygame.mixer.music.stop()
                except Exception:
                    pass
            else:
                proc = self._afplay_proc
                try:
                    if proc and proc.poll() is None:
                        proc.terminate()
                except Exception:
                    pass
        except Exception:
            pass

    def play_jump_sfx(self):
        try:
            if not self._use_afplay:
                if self.jump_sfx:
                    self.jump_sfx.play()
            else:
                if self.jump_sfx_path:
                    subprocess.Popen(['afplay', self.jump_sfx_path])
        except Exception:
            pass


    # ─── Level building helpers ───────────────────────────────────

    def _bridge_single_gaps(self):
        """Fill in single-tile horizontal gaps between platform tiles."""
        try:
            pos_map = {}
            for t in self.platformTiles:
                gx = t.rect.x // TILESIZE
                gy = t.rect.y // TILESIZE
                pos_map[(gx, gy)] = t

            rows = {}
            for (gx, gy) in pos_map:
                rows.setdefault(gy, []).append(gx)

            for gy, xs in rows.items():
                xs_sorted = sorted(xs)
                for i in range(len(xs_sorted) - 1):
                    left = xs_sorted[i]
                    right = xs_sorted[i + 1]
                    if right - left == 2:
                        mx = left + 1
                        if (mx, gy) not in pos_map:
                            src = pos_map.get((left, gy))
                            if src:
                                tile = Tile((mx * TILESIZE, gy * TILESIZE), src.image)
                                self.platformTiles.add(tile)
                                pos_map[(mx, gy)] = tile
        except Exception:
            pass

    def _add_bridge_platforms(self):
        """Add stepping-stone platform tiles to make the level fully connected."""
        ref_surface = None
        for t in self.platformTiles:
            ref_surface = t.image
            break
        if not ref_surface:
            return

        existing = set()
        for t in self.platformTiles:
            existing.add((t.rect.x // TILESIZE, t.rect.y // TILESIZE))

        for gx, gy, width in BRIDGE_PLATFORMS:
            for i in range(width):
                key = (gx + i, gy)
                if key not in existing:
                    tile = Tile((key[0] * TILESIZE, key[1] * TILESIZE), ref_surface)
                    self.platformTiles.add(tile)
                    existing.add(key)

    def _collect_background_layers(self):
        self.background_layers_before = []
        self.background_layers_after = []
        try:
            for lyr in self.levelData.layers:
                lname = (getattr(lyr, 'name', '') or '').lower()
                if ('background' in lname or 'foreground' in lname) and hasattr(lyr, 'tiles'):
                    if 'foreground' in lname or lname.endswith('1'):
                        self.background_layers_after.append(lyr)
                    else:
                        self.background_layers_before.append(lyr)
        except Exception:
            pass

    def _spawn_entities(self):
        hero_pos = (32, 464)
        hero_right = True

        try:
            for obj in self.levelData.objects:
                name = (getattr(obj, 'name', '') or '').lower()
                x = int(getattr(obj, 'x', 0))
                y = int(getattr(obj, 'y', 0))
                obj_h = int(getattr(obj, 'height', TILESIZE))
                bottom_y = y + obj_h

                if name.startswith('player'):
                    hero_pos = (x + int(getattr(obj, 'width', TILESIZE)) // 2, bottom_y)
                    hero_right = 'right' in name
                elif name.startswith('bee'):
                    b = Bee((x, bottom_y), moveRight='right' in name)
                    self.mobs.add(b)
                    self.bees.add(b)
                elif name.startswith('snail'):
                    from ClassSnail import Snail
                    self.mobs.add(Snail((x, bottom_y), moveRight='right' in name))
                elif name.startswith('boar'):
                    from ClassBoar import Boar
                    self.mobs.add(Boar((x, bottom_y), moveRight='right' in name))
        except Exception:
            b1 = Bee((200, 200), moveRight=True)
            b2 = Bee((300, 380), moveRight=False)
            self.mobs.add(b1, b2)
            self.bees.add(b1, b2)

        self.hero.add(Hero(hero_pos, faceRight=hero_right))


    # ─── Game-loop methods ────────────────────────────────────────

    def update(self):
        self.hero.update(self)
        self.mobs.update(self)

        # Smooth camera follow (horizontal only)
        hero = self.hero.sprite
        if hero:
            target_x = hero.xPos - WINDOW_WIDTH // 2
            max_cam = max(0, self.level_pixel_width - WINDOW_WIDTH)
            target_x = max(0.0, min(float(target_x), float(max_cam)))
            self.camera_x += (target_x - self.camera_x) * 0.1

    def draw(self):
        # Sky / static background
        self.background.draw(self.displaySurface)

        cam = int(self.camera_x)

        # Background tile layers (trees, props behind sprites)
        try:
            for lyr in self.background_layers_before:
                for x, y, surf in lyr.tiles():
                    if surf:
                        px = x * TILESIZE - cam
                        if -TILESIZE <= px <= WINDOW_WIDTH:
                            self.displaySurface.blit(surf, (px, y * TILESIZE))
        except Exception:
            pass

        # Platform tiles
        for tile in self.platformTiles:
            px = tile.rect.x - cam
            if -TILESIZE <= px <= WINDOW_WIDTH:
                self.displaySurface.blit(tile.image, (px, tile.rect.y))

        # Hero
        hero = self.hero.sprite
        if hero:
            self.displaySurface.blit(hero.image, (hero.rect.x - cam, hero.rect.y))

        # Mobs
        for mob in self.mobs:
            px = mob.rect.x - cam
            if -80 <= px <= WINDOW_WIDTH + 80:
                self.displaySurface.blit(mob.image, (px, mob.rect.y))

        # Foreground tile layers (trees/props in front of sprites)
        try:
            for lyr in self.background_layers_after:
                for x, y, surf in lyr.tiles():
                    if surf:
                        px = x * TILESIZE - cam
                        if -TILESIZE <= px <= WINDOW_WIDTH:
                            self.displaySurface.blit(surf, (px, y * TILESIZE))
        except Exception:
            pass

    def run(self):
        self.update()
        self.draw()

    def needs_restart(self):
        """True when hero death animation finished or hero fell off level."""
        try:
            hero = self.hero.sprite
        except Exception:
            return False
        if not hero:
            return False
        try:
            if getattr(hero, 'currentState', None) == 'DIE':
                if hero.animationIndex >= len(hero.currentAnimation) - 1:
                    return True
            if getattr(hero, 'yPos', 0) > self.level_pixel_height + 200:
                return True
        except Exception:
            pass
        return False

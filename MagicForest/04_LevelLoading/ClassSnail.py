import pygame
import os
try:
    from image_helper import load_image
except Exception:
    import os, sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from image_helper import load_image
from Config import *


class Snail(pygame.sprite.Sprite):

    def __init__(self, position, moveRight=True):
        super().__init__()
        img_path = SPRITESHEET_PATH + "Mob/Snail/walk-Sheet.png"
        try:
            sheet = load_image(img_path, use_alpha=True)
        except Exception:
            sheet = None

        # build animation frames by slicing the sheet horizontally
        self.frames = []
        if sheet:
            w, h = sheet.get_width(), sheet.get_height()
            if w % h == 0:
                frame_w = h
                count = w // h
            else:
                # fallback to 4 frames
                count = 4
                frame_w = max(1, w // count)
            for i in range(count):
                try:
                    frame = sheet.subsurface(pygame.Rect(i * frame_w, 0, frame_w, h)).convert_alpha()
                except Exception:
                    frame = sheet
                self.frames.append(frame)

        if not self.frames:
            # fallback placeholder
            surf = pygame.Surface((24, 16), pygame.SRCALPHA)
            pygame.draw.ellipse(surf, (120, 60, 20), surf.get_rect())
            self.frames = [surf]

        self.animation_index = 0
        self.animation_speed = 0.12
        self.image = self.frames[0]
        self.rect = self.image.get_rect(bottomleft=position)
        self.movingRight = moveRight
        self.facingRight = moveRight
        self.speed = 1
        self.currentState = 'ALIVE'
        # attempt to load dead animation
        dead_path = SPRITESHEET_PATH + "Mob/Snail/Dead-Sheet.png"
        self.dead_frames = []
        try:
            dead_sheet = load_image(dead_path, use_alpha=True)
            w, h = dead_sheet.get_width(), dead_sheet.get_height()
            frame_w = h if w % h == 0 else (w // 4)
            count = w // frame_w if frame_w else 1
            for i in range(count):
                try:
                    f = dead_sheet.subsurface(pygame.Rect(i * frame_w, 0, frame_w, h)).convert_alpha()
                except Exception:
                    f = dead_sheet
                self.dead_frames.append(f)
        except Exception:
            self.dead_frames = []

    def update(self, level):
        # simple gravity
        try:
            gravity = GRAVITY
        except NameError:
            gravity = 0.6
        if not hasattr(self, 'yVel'):
            self.yVel = 0

        # Check ground ahead before moving: compute probe point just below foot
        # Probe ahead over a small tolerance so tiny gaps don't cause a turn
        dx = int(self.speed) if self.movingRight else -int(self.speed)
        probe_y = self.rect.bottom + 1
        has_ground = False
        try:
            sign = 1 if self.movingRight else -1
            gap_tolerance = 12
            for offset in range(1, gap_tolerance + 1):
                check_x = self.rect.centerx + sign * (abs(dx) + offset)
                for tile in level.platformTiles:
                    if tile.rect.collidepoint((check_x, probe_y)):
                        has_ground = True
                        break
                if has_ground:
                    break
        except Exception:
            has_ground = True

        # If no ground ahead, reverse direction instead of stepping off
        if has_ground:
            self.rect.x += dx
        else:
            self.movingRight = not self.movingRight

        # Turn around at level edges
        level_w = getattr(level, 'level_pixel_width', WINDOW_WIDTH)
        if self.rect.right < 0:
            self.movingRight = True
        if self.rect.left > level_w:
            self.movingRight = False

        # gravity: if not standing on ground, fall
        standing = False
        try:
            for tile in level.platformTiles:
                if tile.rect.collidepoint((self.rect.centerx, self.rect.bottom + 1)):
                    standing = True
                    break
        except Exception:
            standing = True

        if not standing:
            self.yVel += gravity
            self.rect.y += int(self.yVel)
        else:
            self.yVel = 0

        # animate or set single walk image
        if self.currentState == 'DYING':
            # play dead animation, then kill
            if not self.dead_frames:
                self.kill()
                return
            self.animation_index += 0.2
            if self.animation_index >= len(self.dead_frames):
                self.kill()
                return
            self.image = self.dead_frames[int(self.animation_index)]
        else:
            # only update facing image when direction changed
            if self.facingRight != self.movingRight:
                self.facingRight = self.movingRight
            base = self.frames[0]
            self.image = base if not self.facingRight else pygame.transform.flip(base, True, False)

    def die(self):
        if self.currentState != 'DYING':
            self.currentState = 'DYING'
            self.animation_index = 0

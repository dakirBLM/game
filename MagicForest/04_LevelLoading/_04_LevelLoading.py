import pygame
import random
import math
from Config import *
from ClassLevel import Level
from font_helper import GameFont

# ─── Init ─────────────────────────────────────────────────────────
pygame.init()

clock = pygame.time.Clock()
displaySurface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Magic Forest")


# ─── Fonts ────────────────────────────────────────────────────────
font_title      = GameFont(None, 72)
font_subtitle   = GameFont(None, 30)
font_button     = GameFont(None, 36)
font_hint       = GameFont(None, 20)
font_valentine  = GameFont(None, 58)
font_val_sub    = GameFont(None, 28)
font_bubble     = GameFont(None, 22)


# ─── Drawing helpers ──────────────────────────────────────────────

def draw_gradient(surface, top_color, bottom_color):
    for y in range(WINDOW_HEIGHT):
        ratio = y / WINDOW_HEIGHT
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (WINDOW_WIDTH, y))


def draw_text_centered(surface, text, font, color, y, shadow=False):
    if shadow:
        s = font.render(text, True, (0, 0, 0))
        surface.blit(s, ((WINDOW_WIDTH - s.get_width()) // 2 + 2, y + 2))
    rendered = font.render(text, True, color)
    surface.blit(rendered, ((WINDOW_WIDTH - rendered.get_width()) // 2, y))


# ─── Heart shape drawing ─────────────────────────────────────────

def draw_heart(surface, cx, cy, size, color, alpha=255):
    """Draw a filled heart shape at (cx, cy)."""
    heart_surf = pygame.Surface((size * 2 + 2, size * 2 + 2), pygame.SRCALPHA)
    pts = []
    for deg in range(360):
        t = math.radians(deg)
        x = 16 * (math.sin(t) ** 3)
        y = -(13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t))
        pts.append((int(size + x * size / 18), int(size + y * size / 18)))
    if len(pts) > 2:
        pygame.draw.polygon(heart_surf, (*color, alpha), pts)
    surface.blit(heart_surf, (cx - size, cy - size))


# ─── Floating hearts (Valentine menu) ────────────────────────────

class FloatingHeart:
    def __init__(self, initial=True):
        self._randomize(initial)

    def _randomize(self, from_bottom=False):
        self.x = random.randint(20, WINDOW_WIDTH - 20)
        self.y = random.randint(0, WINDOW_HEIGHT) if not from_bottom else WINDOW_HEIGHT + random.randint(10, 60)
        self.size = random.randint(8, 22)
        self.speed = random.uniform(0.4, 1.2)
        self.drift = random.uniform(-0.5, 0.5)
        self.wobble_offset = random.uniform(0, math.pi * 2)
        self.wobble_speed = random.uniform(0.02, 0.05)
        self.color = random.choice([
            (220, 50, 70), (240, 80, 100), (200, 40, 60),
            (255, 100, 120), (180, 30, 50), (255, 130, 160),
        ])
        self.alpha = random.randint(120, 220)

    def update(self, frame):
        self.y -= self.speed
        self.x += self.drift + math.sin(frame * self.wobble_speed + self.wobble_offset) * 0.4
        if self.y < -30:
            self._randomize(from_bottom=True)

    def draw(self, surface, frame):
        draw_heart(surface, int(self.x), int(self.y), self.size, self.color, self.alpha)


# ─── Red particles for game-over ─────────────────────────────────

class Particle:
    def __init__(self, color_lo, color_hi, initial=True):
        self.color_lo = color_lo
        self.color_hi = color_hi
        self._randomize(initial)

    def _randomize(self, from_bottom=False):
        self.x = random.randint(0, WINDOW_WIDTH)
        self.y = random.randint(0, WINDOW_HEIGHT) if not from_bottom else WINDOW_HEIGHT + random.randint(0, 40)
        self.size = random.uniform(2, 5)
        self.speed = random.uniform(0.3, 1.0)
        self.drift = random.uniform(-0.3, 0.3)
        r = random.randint(self.color_lo[0], self.color_hi[0])
        g = random.randint(self.color_lo[1], self.color_hi[1])
        b = random.randint(self.color_lo[2], self.color_hi[2])
        self.color = (r, g, b)

    def update(self):
        self.y -= self.speed
        self.x += self.drift
        if self.y < -10:
            self._randomize(from_bottom=True)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))


# ─── Valentine "No" button that runs away ────────────────────────

class RunawayButton:
    """A button that dodges the mouse cursor when hovered."""
    _messages = [
        "Nope!", "Try again!", "Not today!", "Are you sure?",
        "Think again!", "Wrong button!", "Come on!", "Really?!",
    ]

    def __init__(self, cx, cy, w, h, text, color, hover_color, text_color=(255, 255, 255)):
        self.home_x = cx
        self.home_y = cy
        self.w = w
        self.h = h
        self.rect = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.hovered = False
        self._dodge_count = 0
        self._shake_timer = 0
        self._current_msg = ""
        self._msg_timer = 0

    def update(self, frame):
        mouse = pygame.mouse.get_pos()
        zone = self.rect.inflate(60, 40)
        if zone.collidepoint(mouse):
            dx = self.rect.centerx - mouse[0]
            dy = self.rect.centery - mouse[1]
            dist = math.hypot(dx, dy) or 1
            push = 160
            new_cx = self.rect.centerx + int(dx / dist * push)
            new_cy = self.rect.centery + int(dy / dist * push)
            new_cx = max(self.w // 2 + 10, min(WINDOW_WIDTH - self.w // 2 - 10, new_cx))
            new_cy = max(self.h // 2 + 10, min(WINDOW_HEIGHT - self.h // 2 - 10, new_cy))
            self.rect.centerx = new_cx
            self.rect.centery = new_cy
            self._dodge_count += 1
            if self._dodge_count % 3 == 0:
                self._current_msg = random.choice(self._messages)
                self._msg_timer = 90
        else:
            self.rect.centerx += int((self.home_x - self.rect.centerx) * 0.02)
            self.rect.centery += int((self.home_y - self.rect.centery) * 0.02)

        self.hovered = self.rect.collidepoint(mouse)
        if self._msg_timer > 0:
            self._msg_timer -= 1
        if self._shake_timer > 0:
            self._shake_timer -= 1

    def draw(self, surface, frame):
        sx, sy = 0, 0
        if self._shake_timer > 0:
            sx = random.randint(-3, 3)
            sy = random.randint(-2, 2)

        r = self.rect.move(sx, sy)
        color = self.hover_color if self.hovered else self.color

        pygame.draw.rect(surface, (15, 15, 15), r.move(3, 3), border_radius=14)
        pygame.draw.rect(surface, color, r, border_radius=14)
        border = tuple(min(255, c + 50) for c in color)
        pygame.draw.rect(surface, border, r, 2, border_radius=14)

        label = font_button.render(self.text, True, self.text_color)
        surface.blit(label, (r.centerx - label.get_width() // 2,
                             r.centery - label.get_height() // 2))

        if self._msg_timer > 0 and self._current_msg:
            msg_surf = font_hint.render(self._current_msg, True, (255, 180, 200))
            mx = r.centerx - msg_surf.get_width() // 2
            my = r.top - 30
            surface.blit(msg_surf, (mx, my))

    def clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos))


# ─── Normal Button ────────────────────────────────────────────────

class Button:
    def __init__(self, cx, cy, w, h, text, color, hover_color, text_color=(255, 255, 255)):
        self.rect = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.hovered = False

    def draw(self, surface):
        mouse = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mouse)
        color = self.hover_color if self.hovered else self.color

        pygame.draw.rect(surface, (15, 15, 15), self.rect.move(3, 3), border_radius=14)
        pygame.draw.rect(surface, color, self.rect, border_radius=14)
        border = tuple(min(255, c + 50) for c in color)
        pygame.draw.rect(surface, border, self.rect, 2, border_radius=14)
        label = font_button.render(self.text, True, self.text_color)
        surface.blit(label, (self.rect.centerx - label.get_width() // 2,
                             self.rect.centery - label.get_height() // 2))

    def clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos))


# ─── Speech bubble ────────────────────────────────────────────────

class SpeechBubble:
    """Cute speech bubble that floats above the hero for a set duration."""
    def __init__(self, text, duration_sec=10):
        self.text = text
        self.duration = duration_sec * 60
        self.timer = 0
        self.active = True
        self._text_surf = font_bubble.render(text, True, (60, 30, 30))
        self._padding = 12
        self._bw = self._text_surf.get_width() + self._padding * 2
        self._bh = self._text_surf.get_height() + self._padding * 2

    def update(self):
        if not self.active:
            return
        self.timer += 1
        if self.timer >= self.duration:
            self.active = False

    def draw(self, surface, hero_screen_x, hero_screen_y):
        if not self.active:
            return
        # Fade in / out
        alpha = 255
        if self.timer < 30:
            alpha = int(self.timer / 30.0 * 255)
        elif self.timer > self.duration - 60:
            alpha = int((self.duration - self.timer) / 60.0 * 255)
        alpha = max(0, min(255, alpha))

        bx = hero_screen_x + 30
        by = hero_screen_y - self._bh - 20
        if bx + self._bw > WINDOW_WIDTH - 5:
            bx = hero_screen_x - self._bw - 10
        if by < 5:
            by = 5

        bubble_surf = pygame.Surface((self._bw, self._bh + 14), pygame.SRCALPHA)
        body_color = (255, 245, 240, alpha)
        border_color = (200, 120, 130, alpha)
        pygame.draw.rect(bubble_surf, body_color, (0, 0, self._bw, self._bh), border_radius=10)
        pygame.draw.rect(bubble_surf, border_color, (0, 0, self._bw, self._bh), 2, border_radius=10)

        # Tail pointing down toward the hero
        tail_x = min(25, self._bw // 3)
        pygame.draw.polygon(bubble_surf, body_color, [
            (tail_x, self._bh - 1), (tail_x + 12, self._bh - 1), (tail_x - 4, self._bh + 10)])
        pygame.draw.line(bubble_surf, border_color, (tail_x, self._bh), (tail_x - 4, self._bh + 10), 2)
        pygame.draw.line(bubble_surf, border_color, (tail_x + 12, self._bh), (tail_x - 4, self._bh + 10), 2)

        text_copy = self._text_surf.copy()
        if alpha < 255:
            text_copy.set_alpha(alpha)
        bubble_surf.blit(text_copy, (self._padding, self._padding))

        # Tiny pulsing heart decoration
        heart_pulse = 1.0 + math.sin(self.timer * 0.08) * 0.15
        hsize = int(6 * heart_pulse)
        draw_heart(bubble_surf, self._bw - 14, 10, hsize, (220, 80, 100), alpha)

        surface.blit(bubble_surf, (int(bx), int(by)))


# ─── Pre-build assets ────────────────────────────────────────────

_val_grad = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
draw_gradient(_val_grad, (60, 10, 25), (30, 5, 15))

_death_overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
_death_overlay.fill((0, 0, 0, 180))

hearts        = [FloatingHeart(initial=True) for _ in range(40)]
red_particles = [Particle((150, 30, 20), (255, 80, 60), initial=True) for _ in range(35)]

yes_btn     = Button(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 60, 180, 60,
                     "Y E S  !", (200, 40, 70), (240, 70, 100))
no_btn      = RunawayButton(WINDOW_WIDTH // 2 + 100, WINDOW_HEIGHT // 2 + 60, 180, 60,
                            "N o", (100, 100, 100), (140, 140, 140), (200, 200, 200))
restart_btn = Button(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30, 280, 64,
                     "T R Y   A G A I N", (180, 60, 30), (220, 90, 45))
menu_btn    = Button(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 110, 280, 54,
                     "M A I N   M E N U", (70, 70, 70), (110, 110, 110))


# ─── Game state ───────────────────────────────────────────────────
STATE_MENU      = 'MENU'
STATE_PLAYING   = 'PLAYING'
STATE_GAME_OVER = 'GAME_OVER'

state = STATE_MENU
level = None
speech_bubble = None
frame_count = 0
death_timer = 0
DEATH_DELAY = 60


# ─── Main loop ────────────────────────────────────────────────────
is_running = True
while is_running:
    frame_count += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if state == STATE_PLAYING:
                if level:
                    level.stop_audio()
                    level = None
                speech_bubble = None
                state = STATE_MENU
            else:
                is_running = False

        # ── Valentine menu events ──
        if state == STATE_MENU:
            if yes_btn.clicked(event):
                level = Level(displaySurface)
                speech_bubble = SpeechBubble("Hi ! I am C\u00e9line \u2764", duration_sec=10)
                state = STATE_PLAYING
                death_timer = 0
            if no_btn.clicked(event):
                no_btn._shake_timer = 20
                no_btn._current_msg = random.choice(RunawayButton._messages)
                no_btn._msg_timer = 90

        # ── Game-over events ──
        elif state == STATE_GAME_OVER:
            if restart_btn.clicked(event):
                if level:
                    level.stop_audio()
                level = Level(displaySurface)
                speech_bubble = SpeechBubble("Let's try again ! \u2764", duration_sec=6)
                state = STATE_PLAYING
                death_timer = 0
            elif menu_btn.clicked(event):
                if level:
                    level.stop_audio()
                    level = None
                speech_bubble = None
                state = STATE_MENU
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_r, pygame.K_SPACE, pygame.K_RETURN):
                    if level:
                        level.stop_audio()
                    level = Level(displaySurface)
                    speech_bubble = SpeechBubble("Let's try again ! \u2764", duration_sec=6)
                    state = STATE_PLAYING
                    death_timer = 0

    # ─── Update / Draw ────────────────────────────────────────────

    if state == STATE_MENU:
        # ── Valentine's page ──
        displaySurface.blit(_val_grad, (0, 0))

        for h in hearts:
            h.update(frame_count)
            h.draw(displaySurface, frame_count)

        # Big decorative hearts on sides
        pulse = 1.0 + math.sin(frame_count * 0.04) * 0.08
        draw_heart(displaySurface, 120, WINDOW_HEIGHT // 2 - 30,
                   int(55 * pulse), (180, 40, 60), 80)
        draw_heart(displaySurface, WINDOW_WIDTH - 120, WINDOW_HEIGHT // 2 - 30,
                   int(55 * pulse), (180, 40, 60), 80)

        # Title with gentle bob
        title_y = int(80 + math.sin(frame_count * 0.03) * 5)
        draw_text_centered(displaySurface, "Will You Be",
                           font_valentine, (255, 200, 210), title_y, shadow=True)
        draw_text_centered(displaySurface, "My Valentine ?",
                           font_valentine, (255, 160, 180), title_y + 65, shadow=True)

        # Decorative line with tiny heart
        lw = 300
        lx = (WINDOW_WIDTH - lw) // 2
        ly = title_y + 140
        pygame.draw.line(displaySurface, (200, 80, 100), (lx, ly), (lx + lw, ly), 2)
        draw_heart(displaySurface, WINDOW_WIDTH // 2, ly, 8, (255, 100, 120), 220)

        draw_text_centered(displaySurface, "A magical adventure awaits...",
                           font_val_sub, (220, 170, 180), ly + 14)

        # Buttons
        no_btn.update(frame_count)
        yes_btn.draw(displaySurface)
        no_btn.draw(displaySurface, frame_count)

        draw_text_centered(displaySurface,
                           "Click  YES  to  begin  the  adventure  \u2764",
                           font_hint, (180, 130, 140), WINDOW_HEIGHT - 36)

    elif state == STATE_PLAYING:
        level.run()

        # Speech bubble
        if speech_bubble and speech_bubble.active:
            speech_bubble.update()
            hero = level.hero.sprite
            if hero:
                hx = hero.rect.centerx - int(level.camera_x)
                hy = hero.rect.top
                speech_bubble.draw(displaySurface, hx, hy)

        # Check for death / fall
        if level.needs_restart():
            if death_timer == 0:
                try:
                    level.stop_audio()
                except Exception:
                    pass
            death_timer += 1
            if death_timer >= DEATH_DELAY:
                state = STATE_GAME_OVER
                death_timer = 0

    elif state == STATE_GAME_OVER:
        if level:
            level.draw()

        displaySurface.blit(_death_overlay, (0, 0))

        for p in red_particles:
            p.update()
            p.draw(displaySurface)

        pulse = math.sin(frame_count * 0.035) * 3
        draw_text_centered(displaySurface, "G A M E   O V E R", font_title,
                           (220, 50, 50), int(90 + pulse), shadow=True)

        draw_text_centered(displaySurface, "The forest has claimed another soul ...",
                           font_subtitle, (200, 175, 165), 180)

        lw = 360
        lx = (WINDOW_WIDTH - lw) // 2
        pygame.draw.line(displaySurface, (160, 50, 35), (lx, 220), (lx + lw, 220), 2)

        restart_btn.draw(displaySurface)
        menu_btn.draw(displaySurface)

        draw_text_centered(displaySurface,
                           "Press  R  /  SPACE  to  retry    |    ESC  for  menu",
                           font_hint, (160, 130, 120), WINDOW_HEIGHT - 40)

    pygame.display.flip()
    clock.tick(60)


# ─── Cleanup ──────────────────────────────────────────────────────
if level:
    try:
        level.stop_audio()
    except Exception:
        pass
pygame.quit()

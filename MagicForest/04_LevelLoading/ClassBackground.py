

import pygame
from Config import *
try:
    from image_helper import load_image
except Exception:
    import os, sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from image_helper import load_image


class Background():

    def __init__(self):
        # Create the sky image
        self.skyImage = load_image(SPRITESHEET_PATH + "Background/Background.png", use_alpha=False)
        self.skyImage = pygame.transform.scale(self.skyImage, (WINDOW_WIDTH, WINDOW_HEIGHT))


    def draw(self, displaySurface):
        # Draw sky image
        displaySurface.blit(self.skyImage, (0, 0))

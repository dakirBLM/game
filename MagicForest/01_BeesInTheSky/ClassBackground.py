import pygame
from Config import *
from image_helper import load_image


class Background():

    def __init__(self):
        # Create the sky image. Some pygame builds have trouble with certain PNG
        # decoders on older macOS — try loading the PNG first, then fall back to
        # a BMP version if pygame raises an error.
        png_path = SPRITESHEET_PATH + "Background/Background.png"
        bmp_path = SPRITESHEET_PATH + "Background/Background.bmp"
        try:
            self.skyImage = load_image(png_path, use_alpha=False)
        except Exception:
            # Fall back to BMP (created earlier by Pillow conversion)
            self.skyImage = load_image(bmp_path, use_alpha=False)

        self.skyImage = pygame.transform.scale(self.skyImage, (WINDOW_WIDTH, WINDOW_HEIGHT))


    def draw(self, displaySurface):
        # Draw sky image
        displaySurface.blit(self.skyImage, (0, 0))

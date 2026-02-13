import pygame
from Config import *
from image_helper import load_image


class SpriteSheet():

    def __init__(self, spriteSheetPath, spritePositions):
        image = load_image(spriteSheetPath, use_alpha=True)
        self.sprites = []
        self.spritesFlipped = []
        for position in spritePositions:
            sprite = image.subsurface(pygame.Rect(position))
            self.sprites.append(sprite)
            sprite = pygame.transform.flip(sprite, True, False)
            self.spritesFlipped.append(sprite)


    def getSprites(self, flipped):
        if flipped == True:
            return self.spritesFlipped
        else:
            return self.sprites

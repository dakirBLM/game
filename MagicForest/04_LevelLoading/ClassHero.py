import pygame
from Config import *
from ClassSpriteSheet import SpriteSheet


runSprites = [
    (24, 16, 40, 52),
    (104, 16, 40, 52),
    (184, 16, 40, 52),
    (264, 16, 40, 52),
    (344, 16, 40, 52),
    (424, 16, 40, 52),
    (504, 16, 40, 52),
    (584, 16, 40, 52)
]

idleSprites = [
    (12, 12, 44, 52),
    (76, 12, 44, 52),
    (140, 12, 44, 52),
    (204, 12, 44, 52)
]

attackSprites = [
    (4, 0, 92, 80),
    (100, 0, 92, 80),
    (196, 0, 92, 80),
    (294, 0, 92, 80),
    (388, 0, 92, 80),
    (484, 0, 92, 80),
    (580, 0, 92, 80),
    (676, 0, 92, 80)
]

deathSprites = [
    (0, 0, 64, 56),
    (80, 0, 64, 56),
    (160, 0, 64, 56),
    (240, 0, 64, 56),
    (320, 0, 64, 56),
    (400, 0, 64, 56),
    (480, 0, 64, 56),
    (560, 0, 64, 56)
]



class Hero(pygame.sprite.Sprite):

    def __init__(self, position, faceRight):
        super().__init__()

        # Brown tint to give the character a warmer / brown look
        _tint = (160, 110, 60)

        # Load spritesheets
        idleSpriteSheet = SpriteSheet(SPRITESHEET_PATH + "Character/Idle/Idle-Sheet.png", idleSprites, tint=_tint)
        runSpriteSheet = SpriteSheet(SPRITESHEET_PATH + "Character/Run/Run-Sheet.png", runSprites, tint=_tint)
        attackSpriteSheet = SpriteSheet(SPRITESHEET_PATH + "Character/Attack-01/Attack-01-Sheet.png", attackSprites, tint=_tint)
        deathSpriteSheet = SpriteSheet(SPRITESHEET_PATH + "Character/Dead/Dead-Sheet.png", deathSprites, tint=_tint)

        self.spriteSheets = {
            'IDLE'   : idleSpriteSheet,
            'RUN'    : runSpriteSheet,
            'ATTACK' : attackSpriteSheet,
            'DIE'    : deathSpriteSheet
        }

        self.animationIndex = 0
        self.facingRight = faceRight
        self.currentState = 'IDLE'
        self.xDir = 0
        self.speed = SPEED_HERO
        self.xPos = position[0]
        self.yPos = position[1]
        self.yVel = 0.0
        self.onGround = False
        # Jump velocity (negative = up)
        self._jump_speed = -12.0


    def update(self, level):
        self.previousState = self.currentState
        self.xDir = 0

        # get key status
        if self.currentState != 'ATTACK' and self.currentState != 'DIE':
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                self.currentState = 'ATTACK'
            elif keys[pygame.K_LEFT]:
                self.xDir = -1
                self.facingRight = False
                self.currentState = 'RUN'
            elif keys[pygame.K_RIGHT]:
                self.xDir = 1
                self.facingRight = True
                self.currentState = 'RUN'
            else:
                self.currentState = 'IDLE'

        # Select animation for current player action (idle, run, jump, fall, etc.)
        self.selectAnimation()

        # Start from beginning of a new animation
        if self.previousState != self.currentState:
            self.animationIndex = 0

        # Select the image
        self.image = self.currentAnimation[int(self.animationIndex)]

        # Select a rect size depending on the current animation
        # (xPos, yPos) = bottom-center position of the sprite
        if self.currentState == 'IDLE':
            self.rect = pygame.Rect(self.xPos - 22, self.yPos - 52, 44, 52)
        elif self.currentState == 'RUN':
            self.rect = pygame.Rect(self.xPos - 20, self.yPos - 48, 40, 48)
        elif self.currentState == 'ATTACK':
            self.rect = pygame.Rect(self.xPos - 44, self.yPos - 64, 88, 64)
        elif self.currentState == 'DIE':
            self.rect = pygame.Rect(self.xPos - 32, self.yPos - 48, 64, 48)

        # Play animation until end of current animation is reached
        self.animationIndex += self.animationSpeed
        if self.animationIndex >= len(self.currentAnimation):
            if self.currentState == 'DIE':
                self.animationIndex = len(self.currentAnimation) - 1
            else:
                self.animationIndex = 0
                self.currentState = 'IDLE'

        self.moveHorizontal(level)
        # Apply vertical movement (gravity, jumping, falling)
        self.moveVertical(level)

        # Handle collisions with enemies (check all mobs/bees)
        self.checkEnemyCollisions(level)


    def selectAnimation(self):
        self.animationSpeed = ANIMSPEED_HERO_DEFAULT
        if self.currentState == 'IDLE':
            self.animationSpeed = ANIMSPEED_HERO_IDLE

        spriteSheet = self.spriteSheets[self.currentState]
        self.currentAnimation = spriteSheet.getSprites(flipped = not self.facingRight)


    def moveHorizontal(self, level):
        self.rect.centerx += self.xDir * self.speed

        # Do not walk outside level (use full level width, not window)
        level_w = getattr(level, 'level_pixel_width', WINDOW_WIDTH)
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > level_w:
            self.rect.right = level_w

        self.xPos = self.rect.centerx


    def moveVertical(self, level):
        # Handle jump input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and self.onGround:
            self.yVel = self._jump_speed
            self.onGround = False
            # Play jump sound if available on the level
            try:
                if hasattr(level, 'play_jump_sfx'):
                    level.play_jump_sfx()
            except Exception:
                pass

        # Apply gravity
        try:
            gravity = GRAVITY
        except NameError:
            gravity = 0.6
        self.yVel += gravity

        # Move vertically using yPos as bottom coordinate
        self.yPos += self.yVel

        # Recompute rect based on current state (yPos is bottom-center)
        if self.currentState == 'IDLE':
            self.rect = pygame.Rect(self.xPos - 22, self.yPos - 52, 44, 52)
        elif self.currentState == 'RUN':
            self.rect = pygame.Rect(self.xPos - 20, self.yPos - 48, 40, 48)
        elif self.currentState == 'ATTACK':
            self.rect = pygame.Rect(self.xPos - 44, self.yPos - 64, 88, 64)
        elif self.currentState == 'DIE':
            self.rect = pygame.Rect(self.xPos - 32, self.yPos - 48, 64, 48)

        # Resolve collisions with platform tiles
        collided = pygame.sprite.spritecollide(self, level.platformTiles, False)
        if collided:
            for tile in collided:
                # Falling onto a platform
                if self.yVel > 0 and self.rect.bottom > tile.rect.top:
                    self.rect.bottom = tile.rect.top
                    self.yVel = 0
                    self.onGround = True
                # Hitting head on a platform above
                elif self.yVel < 0 and self.rect.top < tile.rect.bottom:
                    self.rect.top = tile.rect.bottom
                    self.yVel = 0
            # Keep yPos in sync with rect bottom
            self.yPos = self.rect.bottom
        else:
            # No collision -> in the air
            self.onGround = False


    def die(self):
        if self.currentState != 'DIE':
            self.currentState = 'DIE'
            self.animationIndex = 0


    def checkEnemyCollisions(self, level):
        # Build a combined sprite group of enemies (mobs + bees) for collisions
        enemies = pygame.sprite.Group()
        try:
            if hasattr(level, 'mobs') and level.mobs:
                for s in level.mobs:
                    enemies.add(s)
        except Exception:
            pass
        try:
            if hasattr(level, 'bees') and level.bees:
                for s in level.bees:
                    enemies.add(s)
        except Exception:
            pass

        # Check for collisions between hero and all enemies in the combined group
        collidedSprites = pygame.sprite.spritecollide(self, enemies, False)
        for enemy in collidedSprites:
            if self.currentState == 'ATTACK':
                if self.facingRight == True:
                    if enemy.rect.left < self.rect.right - 30:
                        enemy.die()
                else:
                    if enemy.rect.right > self.rect.left + 30:
                        enemy.die()
            else:
                if enemy.currentState != 'DYING':
                    if self.rect.left < enemy.rect.left:  # Collision on right side
                        if self.rect.right > enemy.rect.left + 16:
                            self.die()
                    elif self.rect.right > enemy.rect.right:  # Collision on left side
                        if self.rect.left < enemy.rect.right - 16:
                            self.die()

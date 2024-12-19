import pygame
from settings import *

class Character:
    def __init__(self):
        self.sprite_sheet = pygame.image.load('media/sprite-person.png').convert_alpha()
        self.frame_width = 64
        self.frame_height = 64
        self.directions = ["down", "left", "right", "up"]
        self.frames = self.load_frames()

        self.image = self.frames["down"][0]
        self.rect = self.image.get_rect()
        self.rect.center = (400, 300)
        self.lives = 5
        self.current_direction = "down"
        self.animation_index = 0
        self.animation_speed = 0.1
        self.animation_counter = 0
        self.invincible = False
        self.invincible_timer = 0
        self.speed = CHARACTER_SPEED # Přidán atribut rychlosti

    def load_frames(self):
        frames = {direction: [] for direction in self.directions}
        for i, direction in enumerate(self.directions):
            for j in range(4):
                frame = self.sprite_sheet.subsurface(
                    pygame.Rect(j * self.frame_width, i * self.frame_height, self.frame_width, self.frame_height)
                )
                frames[direction].append(frame)
        return frames

    def update(self):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        direction = None

        if keys[pygame.K_LEFT]:
            dx = -self.speed
            direction = "left"
        if keys[pygame.K_RIGHT]:
            dx = self.speed
            direction = "right"
        if keys[pygame.K_UP]:
            dy = -self.speed
            direction = "up"
        if keys[pygame.K_DOWN]:
            dy = self.speed
            direction = "down"

        self.rect.x += dx
        self.rect.y += dy

        # Kontrola hranic okna
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

        if direction:
            self.current_direction = direction
            self.animate()
        else:
            self.animation_index = 0
            self.image = self.frames[self.current_direction][0]

        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False

    def animate(self):
        self.animation_counter += self.animation_speed
        if self.animation_counter >= 1:
            self.animation_counter = 0
            self.animation_index = (self.animation_index + 1) % len(self.frames[self.current_direction])
            self.image = self.frames[self.current_direction][self.animation_index]

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        #pygame.draw.rect(screen, (255, 255, 255), self.rect, 1)  # Vykreslení hitboxu postavy

        # Vykreslení hitboxu pro kontrolu
       #character_hitbox = pygame.Rect(self.rect.x + self.rect.width // 6, self.rect.y + self.rect.height // 6, self.rect.width * 2 // 3, self.rect.height * 2 // 3)
       # pygame.draw.rect(screen, (0, 255, 0), character_hitbox, 1)  # Vykreslení hitboxu postavy

    def hit(self):
        if not self.invincible:
            self.lives -= 1
            self.invincible = True
            self.invincible_timer = FPS * 2  # 2 sekundy při 60 FPS
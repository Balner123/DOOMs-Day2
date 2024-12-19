import pygame
import random
from settings import *

class Asteroid:
    def __init__(self):
        self.scale = random.uniform(RANDOM_MIN,RANDOM_MAX)  # Náhodné zvětšení asteroidu
        self.sprite_sheet = pygame.image.load('media/asteroid.png').convert_alpha()
        self.target_image = pygame.image.load('media/target.png').convert_alpha()
        self.target_image = pygame.transform.scale(self.target_image, ((self.target_image.get_width() // 5)*self.scale, (self.target_image.get_height() // 5)*self.scale))
        self.frame_width = self.sprite_sheet.get_width() // 4
        self.frame_height = self.sprite_sheet.get_height()
        self.scaled_width = (self.frame_width // 5)*self.scale
        self.scaled_height = (self.frame_height // 5)*self.scale
        self.frames = self.load_frames()
        self.rect = self.frames[0].get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH)
        self.rect.y = -self.rect.height
        self.target_x = self.rect.x
        self.target_y = random.randint(0, SCREEN_HEIGHT)
        self.speed = ASTEROID_SPEED / self.scale # Konstantní rychlost
        self.animation_index = 0
        self.animation_speed = 0.15
        self.animation_counter = 0
        self.image = self.frames[0]  # Inicializace atributu image
        self.landed = False

    def load_frames(self):
        frames = []
        for i in range(4):  # 4 sloupce
            frame = self.sprite_sheet.subsurface(
                pygame.Rect(i * self.frame_width, 0, self.frame_width, self.frame_height)
            )
            scaled_frame = pygame.transform.scale(frame, (self.scaled_width, self.scaled_height))
            frames.append(scaled_frame)
        return frames

    def update(self):
        if not self.landed:
            self.rect.y += self.speed
            if self.rect.y >= self.target_y:
                self.rect.y = self.target_y
                self.landed = True
                return True  # Signalizuje, že asteroid dopadl
        self.animate()
        return False

    def animate(self):
        self.animation_counter += self.animation_speed
        if self.animation_counter >= 1:
            self.animation_counter = 0
            self.animation_index = (self.animation_index + 1) % len(self.frames)
            self.image = self.frames[self.animation_index]

    def draw(self, screen):
        if not self.landed:
            target_rect = self.target_image.get_rect(center=(self.target_x, self.target_y))
            screen.blit(self.target_image, target_rect)
        offset_rect = self.rect.copy()
        offset_rect.y -= self.rect.height
        offset_rect.x -= self.rect.width // 2
        screen.blit(self.image, offset_rect)
import pygame
import random
from settings import *

class Asteroid:
    def __init__(self):
        self.scale = random.uniform(RANDOM_MIN, RANDOM_MAX)  # Náhodné zvětšení asteroidu
        self.sprite_sheet = pygame.image.load('media/asteroid.png').convert_alpha()
        self.frame_width = self.sprite_sheet.get_width() // 4
        self.frame_height = self.sprite_sheet.get_height()
        self.scaled_width = (self.frame_width // 5) * self.scale
        self.scaled_height = (self.frame_height // 5) * self.scale
        self.frames = self.load_frames()
        self.rect = self.frames[0].get_rect()
        self.rect.x = random.randint(ROZMEZI_X, SCREEN_WIDTH-ROZMEZI_X)
        self.rect.y = -self.rect.height
        self.speed = ASTEROID_SPEED / self.scale  # Rychlost je inverzně úměrná velikosti
        self.animation_index = 0
        self.animation_speed = 0.15
        self.animation_counter = 0
        self.image = self.frames[0]  # Inicializace atributu image
        self.landed = False
        self.delay_timer = 40  # Počet snímků pro zpoždění před pohybem
        self.target = None  # Atribut pro uložení cíle

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
        self.animation_counter += self.animation_speed
        if self.animation_counter >= 1:
            self.animation_counter = 0
            self.animation_index = (self.animation_index + 1) % len(self.frames)
            self.image = self.frames[self.animation_index]

        if self.delay_timer > 0:
            self.delay_timer -= 1
        else:
            self.rect.y += self.speed
            if self.rect.y >= self.target_y:
                self.landed = True

        return self.landed

    def draw(self, surface):
        offset_rect = self.rect.copy()
        offset_rect.x -= self.rect.width // 2  # Posun vlevo o čtvrtinu šířky
        offset_rect.y -= self.rect.height * 0.75  # Posun nahoru o polovinu výšky
        surface.blit(self.image, offset_rect)
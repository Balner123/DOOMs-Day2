import pygame
import math
import random
from settings import *

class Explosion:
    def __init__(self, position, scale):
        self.scale = scale
        self.sprite_sheet = pygame.image.load('media/explosion.png').convert_alpha()
        self.frame_width = self.sprite_sheet.get_width() // 4
        self.frame_height = self.sprite_sheet.get_height() // 2
        self.scaled_width = (self.frame_width // 5)*scale
        self.scaled_height = (self.frame_height // 5)*scale
        self.frames = self.load_frames()
        self.rect = self.frames[0].get_rect(center=position)
        self.frame = 0
        self.finished = False
        self.animation_speed = 0.2  # Zpomalení animace
        self.animation_counter = 0
        self.crater_created = False
        self.hit_detected = False  # Přidáno pro sledování detekce zásahu
        
        self.posun_y = 0.85 # Posun nahoru
        self.posun_x = 0.25 # Posun vlevo

    def load_frames(self):
        frames = []
        for i in range(2):  # 2 řádky
            for j in range(4):  # 4 sloupce
                frame = self.sprite_sheet.subsurface(
                    pygame.Rect(j * self.frame_width, i * self.frame_height, self.frame_width, self.frame_height)
                )
                scaled_frame = pygame.transform.scale(frame, (self.scaled_width, self.scaled_height))
                frames.append(scaled_frame)
        return frames

    def update(self):
        self.animation_counter += self.animation_speed
        if self.animation_counter >= 1:
            self.animation_counter = 0
            self.frame += 1
            if self.frame >= len(self.frames):
                self.finished = True
            elif self.frame == 3:
                self.crater_created = True

    def get_offset_rect(self):
        offset_rect = self.rect.copy()
        offset_rect.x -= self.rect.width * self.posun_x  # Posun více vlevo
        offset_rect.y -= self.rect.height * self.posun_y  # Posun ještě více nahoru
        return offset_rect

    def draw(self, screen):
        if not self.finished:
            offset_rect = self.get_offset_rect()
            screen.blit(self.frames[self.frame], offset_rect)
           # pygame.draw.rect(screen, (255, 255, 255), offset_rect, 1)  # Vykreslení hitboxu exploze

            # Vykreslení hitboxů pro kontrolu
            #explosion_hitbox = pygame.Rect(offset_rect.x + offset_rect.width // 6, offset_rect.y + offset_rect.height // 6, offset_rect.width * 2 // 3, offset_rect.height * 2 // 3)
            #explosion_hitbox.y += explosion_hitbox.height // 2  # Posun hitboxu o půl výšky dolů
            #explosion_hitbox.inflate_ip(-explosion_hitbox.width // 4, -explosion_hitbox.height // 4)  # Zmenšení hitboxu o 1/4
            #pygame.draw.rect(screen, (255, 0, 0), explosion_hitbox, 1)  # Vykreslení hitboxu exploze

    def has_collided(self, character):
        if self.hit_detected or self.frame > 4:
            return False
        offset_rect = self.get_offset_rect()
        explosion_hitbox = pygame.Rect(offset_rect.x + offset_rect.width // 6, offset_rect.y + offset_rect.height // 6, offset_rect.width * 2 // 3, offset_rect.height * 2 // 3)
        explosion_hitbox.y += explosion_hitbox.height // 2  # Posun hitboxu o půl výšky dolů
        explosion_hitbox.inflate_ip(-explosion_hitbox.width // 4, -explosion_hitbox.height // 4)  # Zmenšení hitboxu o 1/4
        character_hitbox = pygame.Rect(character.rect.x + character.rect.width // 6, character.rect.y + character.rect.height // 6, character.rect.width * 2 // 3, character.rect.height * 2 // 3)
        if explosion_hitbox.colliderect(character_hitbox):
            self.hit_detected = True
            return True
        return False
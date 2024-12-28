import pygame
import time
from settings import *

class Crater:
    def __init__(self, position, scale):
        self.image = pygame.image.load('media/crater.png').convert_alpha()
        self.scaled_width = (self.image.get_width() // 5)*scale
        self.scaled_height = (self.image.get_height() // 5)*scale
        self.image = pygame.transform.scale(self.image, (self.scaled_width, self.scaled_height))
        self.rect = self.image.get_rect(center=position)
        self.creation_time = time.time()  # Zaznamenání času vytvoření kráteru

    def draw(self, screen):
        offset_rect = self.rect.copy()
        offset_rect.y -= self.rect.height * 0.8  # Posun o jednu a půl výšku kráteru nahoru
        offset_rect.x -= self.rect.width * 0.5  # Posun o 0.6 šířky kráteru vlevo
        screen.blit(self.image, offset_rect)

    def is_expired(self):
        return time.time() - self.creation_time > CRATERLIVE  # Kontrola, zda uplynulo 20 sekund
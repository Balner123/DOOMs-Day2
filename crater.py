import pygame

class Crater:
    def __init__(self, position, scale):
        self.image = pygame.image.load('media/crater.png').convert_alpha()
        self.scaled_width = (self.image.get_width() // 5)*scale
        self.scaled_height = (self.image.get_height() // 5)*scale
        self.image = pygame.transform.scale(self.image, (self.scaled_width, self.scaled_height))
        self.rect = self.image.get_rect(center=position)

    def draw(self, screen):
        offset_rect = self.rect.copy()
        offset_rect.y -= self.rect.height * 1.5  # Posun o jednu a půl výšku kráteru nahoru
        offset_rect.x -= self.rect.width * 0.6  # Posun o 0.6 šířky kráteru vlevo
        screen.blit(self.image, offset_rect)

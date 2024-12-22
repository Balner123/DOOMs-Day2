import pygame

class Target:
    def __init__(self, x, y, scale):
        self.image = pygame.image.load('media/target.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, ((self.image.get_width() // 5) * scale, (self.image.get_height() // 5) * scale))
        self.rect = self.image.get_rect(center=(x, y))

    def draw(self, surface):
        offset_rect = self.rect.copy()
        offset_rect.x -= self.rect.width * 0.0  # Posun vlevo o čtvrtinu šířky
        surface.blit(self.image, offset_rect)
import pygame
from settings import *

class Target:
    def __init__(self, x, y, scale):
        # Načtení sprite sheetu místo jednoho obrázku
        self.sprite_sheet = pygame.image.load('media/target_sprite2.png').convert_alpha()
        
        # Rozměry jednoho snímku a mřížky
        self.frame_width = 512
        self.frame_height = 512
        self.grid_cols = 5
        self.grid_rows = 4
        
        # Vytvoření seznamu všech snímků
        self.frames = []
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                # Výřez jednoho snímku ze sprite sheetu
                x_pos = col * self.frame_width
                y_pos = row * self.frame_height
                
                frame = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
                frame.blit(self.sprite_sheet, (0, 0), (x_pos, y_pos, self.frame_width, self.frame_height))
                
                # Změna velikosti snímku podle zadaného měřítka
                scaled_width = (self.frame_width // 5) * scale
                scaled_height = (self.frame_height // 5) * scale
                frame = pygame.transform.scale(frame, (scaled_width, scaled_height))
                
                self.frames.append(frame)
        
        # Proměnné pro animaci
        self.current_frame = 0
        self.animation_speed = TARGETANIMATIONSPEED  # Rychlost animace (sekundy mezi snímky)
        self.timer = 0
        
        # Vytvoření rect podle prvního snímku
        self.rect = self.frames[0].get_rect(center=(x, y))

    def update(self, dt):
        # Aktualizace animace
        self.timer += dt
        if self.timer >= self.animation_speed:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.timer = 0

    def draw(self, surface):
        offset_rect = self.rect.copy()
        offset_rect.x -= self.rect.width * 0.0
        # Vykreslení aktuálního snímku místo statického obrázku
        surface.blit(self.frames[self.current_frame], offset_rect)
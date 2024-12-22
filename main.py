import pygame
import random
from character import Character
from asteroid import Asteroid
from target import Target
from explosion import Explosion
from crater import Crater
from settings import *

# Inicializace Pygame
pygame.init()

# Nastavení obrazovky
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Falling Star !")

# Načtení a škálování pozadí
background = pygame.image.load('media/background.png')
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
blood_screen = pygame.image.load('media/blood_screen.png').convert_alpha()

# Inicializace fontu
font = pygame.font.Font(None, 36)

def apply_shake_effect(intensity):
    shake_x = random.randint(-intensity, intensity)
    shake_y = random.randint(-intensity, intensity)
    return shake_x, shake_y

# Hlavní smyčka hry
def main():
    clock = pygame.time.Clock()
    running = True

    # Vytvoření objektů
    player = Character()
    asteroids = []
    targets = []
    explosions = []
    craters = []
    blood_screen_timer = 0
    hit_count = 0

    # Nastavení časovače pro generování asteroidů
    pygame.time.set_timer(pygame.USEREVENT, ASTEROID_SPAWN_DELAY)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.USEREVENT:
                asteroid = Asteroid()
                target = Target(asteroid.rect.x, random.randint(ROZMEZI_Y, SCREEN_HEIGHT-ROZMEZI_Y), asteroid.scale)
                asteroid.target_y = target.rect.y
                asteroid.target = target  # Uložení cíle do asteroidu
                asteroids.append(asteroid)
                targets.append(target)

        # Aktualizace
        player.update()
        if player.lives <= 0:
            running = False  # Ukončení hlavní smyčky hry, pokud hráč nemá žádné životy

        for asteroid in asteroids[:]:
            if asteroid.update():
                explosions.append(Explosion(asteroid.rect.center, asteroid.scale))
                targets.remove(asteroid.target)  # Odstranění cíle spojeného s asteroidem
                asteroids.remove(asteroid)

        for explosion in explosions[:]:
            explosion.update()
            if explosion.has_collided(player) and not player.invincible:
                player.hit()
                blood_screen_timer = FPS * INVINCIBILITY  
                hit_count += 1
            if explosion.crater_created and not explosion.finished:
                craters.append(Crater(explosion.rect.center, explosion.scale))
                explosion.crater_created = False
            if explosion.finished:
                explosions.remove(explosion)

        # Vykreslení na povrch
        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        surface.blit(background, (0, 0))

        for crater in craters:
            crater.draw(surface)
        for target in targets:
            target.draw(surface)
        player.draw(surface)
        for asteroid in asteroids:
            asteroid.draw(surface)
        for explosion in explosions:
            explosion.draw(surface)

        # Vykreslení blood_screen.png
        if blood_screen_timer > 0:
            blood_screen_timer -= 1
            scaled_blood_screen = pygame.transform.scale(blood_screen, (SCREEN_WIDTH, SCREEN_HEIGHT))
            surface.blit(scaled_blood_screen, (0, 0))

        # Vykreslení počítadla zásahů
        hit_count_text = font.render(f"Zásahy: {hit_count}", True, (255, 255, 255))
        surface.blit(hit_count_text, (10, 10))

        # Aplikace otřesů na celý povrch
        shake_x, shake_y = apply_shake_effect(SHAKE_INTENSITY)
        screen.blit(surface, (shake_x, shake_y))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
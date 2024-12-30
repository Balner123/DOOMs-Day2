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
skull_image = pygame.image.load('media/skull.png').convert_alpha()
skull_image = pygame.transform.scale(skull_image, (40*1.5, 45*1.5))  # Zvětšení velikosti lebky třikrát

# Inicializace fontu
font = pygame.font.Font(None, 36)

def apply_shake_effect(intensity):
    shake_x = random.randint(-intensity, intensity)
    shake_y = random.randint(-intensity, intensity)
    return shake_x, shake_y

def draw_text(surface, text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    # Vykreslení černého obdélníku pod textem
    pygame.draw.rect(surface, (0, 0, 0), text_rect.inflate(20, 10))
    surface.blit(text_surface, text_rect)

def format_time(elapsed_time):
    minutes = elapsed_time // 60000
    seconds = (elapsed_time % 60000) // 1000
    milliseconds = (elapsed_time % 1000) // 10
    return f"{minutes:02}:{seconds:02}:{milliseconds:02}"

def main_menu():
    # Načtení a škálování pozadí
    background = pygame.image.load('media/game.png')
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

    while True:
        screen.blit(background, (0, 0))
        draw_text(screen, "Falling Star", font, (255, 255, 255), SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
        draw_text(screen, "Press ENTER to PLAY", font, (255, 255, 255), SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        draw_text(screen, "Press ESC to EXIT", font, (255, 255, 255), SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()

        pygame.display.flip()

def game_over_screen(final_time):
    while True:
        screen.fill((0, 0, 0))
        draw_text(screen, "Game Over", font, (255, 255, 255), SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
        draw_text(screen, f"Final Time: {final_time}", font, (255, 255, 255), SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        draw_text(screen, "Press ENTER to CONTINUE", font, (255, 255, 255), SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return

        pygame.display.flip()

def main_game():
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
    start_time = pygame.time.get_ticks()  # Zaznamenání času spuštění hry
    last_difficulty_increase_time = start_time  # Zaznamenání času posledního zvýšení obtížnosti

    # Nastavení časovače pro generování asteroidů
    asteroid_spawn_delay = ASTEROID_SPAWN_DELAY
    pygame.time.set_timer(pygame.USEREVENT, asteroid_spawn_delay)

    asteroid_speed = ASTEROID_SPEED
    crater_life = CRATERLIVE

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.USEREVENT:
                asteroid = Asteroid()
                asteroid.speed = asteroid_speed / asteroid.scale  # Nastavení rychlosti asteroidu
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

        # Odstranění kráterů po uplynutí jejich životnosti
        for crater in craters[:]:
            if crater.is_expired():
                craters.remove(crater)

        # Zvýšení obtížnosti
        current_time = pygame.time.get_ticks()
        if current_time - last_difficulty_increase_time > DIFFICULTY_INCREASE_INTERVAL:
            last_difficulty_increase_time = current_time
            asteroid_speed += ASTEROID_SPEED_INCREMENT
            asteroid_spawn_delay = max(50, asteroid_spawn_delay - ASTEROID_SPAWN_DELAY_DECREMENT)
            crater_life = max(5, crater_life - CRATER_LIFE_DECREMENT)
            pygame.time.set_timer(pygame.USEREVENT, asteroid_spawn_delay)

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

        # Vykreslení času od spuštění hry
        elapsed_time = pygame.time.get_ticks() - start_time
        time_text = font.render(f"Čas: {format_time(elapsed_time)}", True, (255, 255, 255))
        surface.blit(time_text, (10, 10))

        # Vykreslení lebek za každý zásah
        for i in range(hit_count):
            surface.blit(skull_image, (10 + i * 50, 40)) # Posun lebek o 60 pixelů doprava

        # Aplikace otřesů na celý povrch
        shake_x, shake_y = apply_shake_effect(SHAKE_INTENSITY)
        screen.blit(surface, (shake_x, shake_y))

        pygame.display.flip()
        clock.tick(FPS)

    final_time = format_time(elapsed_time)
    return final_time

def main():
    while True:
        main_menu()
        final_time = main_game()
        game_over_screen(final_time)

if __name__ == "__main__":
    main()

pygame.quit()
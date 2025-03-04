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
pygame.display.set_caption("DOOM's DAY")

# Načtení a škálování pozadí
background = pygame.transform.scale(pygame.image.load('media/background.png'), (SCREEN_WIDTH, SCREEN_HEIGHT))
blood_screen = pygame.image.load('media/blood_screen.png').convert_alpha()
skull_image = pygame.transform.scale(pygame.image.load('media/skull.png').convert_alpha(), (60, 67.5))

# Inicializace fontu
font = pygame.font.Font(None, 36)

def apply_shake_effect(intensity):
    return random.randint(-intensity, intensity), random.randint(-intensity, intensity)

def draw_text(surface, text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    pygame.draw.rect(surface, (0, 0, 0), text_rect.inflate(20, 10))
    surface.blit(text_surface, text_rect)

def format_time(elapsed_time):
    minutes = elapsed_time // 60000
    seconds = (elapsed_time % 60000) // 1000
    milliseconds = (elapsed_time % 1000) // 10
    return f"{minutes:02}:{seconds:02}:{milliseconds:02}"

def main_menu():
    background = pygame.transform.scale(pygame.image.load('media/game.png'), (SCREEN_WIDTH, SCREEN_HEIGHT))
    while True:
        screen.blit(background, (0, 0))
        draw_text(screen, "Doom's day", font, (255, 255, 255), SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
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
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return
        pygame.display.flip()

def main_game():
    clock = pygame.time.Clock()
    running, paused = True, False
    player = Character()
    asteroids, targets, explosions, craters = [], [], [], []
    blood_screen_timer, hit_count, start_time = 0, 0, pygame.time.get_ticks()
    pause_start_time, total_pause_time, last_difficulty_increase_time = 0, 0, start_time
    giant_asteroid_spawned, giant_explosion, giant_asteroid_landed, white_screen_timer = False, None, False, 0
    asteroid_spawn_delay, asteroid_speed, crater_life = ASTEROID_SPAWN_DELAY, ASTEROID_SPEED, CRATERLIVE
    pygame.time.set_timer(pygame.USEREVENT, asteroid_spawn_delay)

    while running:
        current_time = pygame.time.get_ticks()
        elapsed_time_seconds = (current_time - start_time - (total_pause_time if not paused else total_pause_time + (current_time - pause_start_time))) / 1000
        if elapsed_time_seconds >= ENDARIVALLTIME and not giant_asteroid_spawned and not paused:
            giant_asteroid = Asteroid()
            giant_asteroid.scale = RANDOM_MAX * GIANT_ASTEROID_SCALE
            giant_asteroid.scaled_width = (giant_asteroid.frame_width // 5) * giant_asteroid.scale
            giant_asteroid.scaled_height = (giant_asteroid.frame_height // 5) * giant_asteroid.scale
            giant_asteroid.frames = giant_asteroid.load_frames()
            giant_asteroid.image = giant_asteroid.frames[0]
            giant_asteroid.rect.width, giant_asteroid.rect.height = giant_asteroid.scaled_width, giant_asteroid.scaled_height
            center_target = Target(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, giant_asteroid.scale)
            giant_asteroid.target_y, giant_asteroid.target = center_target.rect.y, center_target
            giant_asteroid.rect.x, giant_asteroid.rect.y = SCREEN_WIDTH // 2, -giant_asteroid.rect.height
            giant_asteroid.speed = asteroid_speed / (giant_asteroid.scale * GIANT_ASTEROID_SPEED_FACTOR)
            giant_asteroid.target_center, giant_asteroid.is_giant = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), True
            asteroids.append(giant_asteroid)
            targets.append(center_target)
            giant_asteroid_spawned = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and not giant_asteroid_landed:
                if paused:
                    total_pause_time += pygame.time.get_ticks() - pause_start_time
                else:
                    pause_start_time = pygame.time.get_ticks()
                paused = not paused
            elif event.type == pygame.USEREVENT and not paused and not giant_asteroid_landed:
                asteroid = Asteroid()
                asteroid.speed = asteroid_speed / asteroid.scale
                target = Target(asteroid.rect.x, random.randint(ROZMEZI_Y, SCREEN_HEIGHT-ROZMEZI_Y), asteroid.scale)
                asteroid.target_y, asteroid.target, asteroid.is_giant = target.rect.y, target, False
                asteroids.append(asteroid)
                targets.append(target)

        if giant_asteroid_landed:
            if white_screen_timer > 0:
                white_screen_timer -= 1
            else:
                player.lives = 0
                running = False
        elif not paused:
            player.update()
            if player.lives <= 0:
                running = False

            for asteroid in asteroids[:]:
                if asteroid.update():
                    if hasattr(asteroid, 'is_giant') and asteroid.is_giant:
                        explosion_x, explosion_y = asteroid.rect.centerx - (asteroid.rect.width // 19), asteroid.rect.centery + (asteroid.rect.height // 19)
                        giant_explosion = Explosion((explosion_x, explosion_y), asteroid.scale)
                        explosions.append(giant_explosion)
                        targets.remove(asteroid.target)
                        asteroids.remove(asteroid)
                    else:
                        explosions.append(Explosion(asteroid.rect.center, asteroid.scale))
                        targets.remove(asteroid.target)
                        asteroids.remove(asteroid)

            dt = clock.get_time() / 1000.0
            for target in targets:
                target.update(dt)

            for explosion in explosions[:]:
                explosion.update()
                if explosion == giant_explosion and explosion.frame >= GIANT_ASTEROID_EXPLOSION_FRAME and not giant_asteroid_landed:
                    giant_asteroid_landed = True
                    white_screen_timer = WHITE_SCREEN_DURATION * FPS
                if explosion.has_collided(player) and not player.invincible:
                    player.hit()
                    blood_screen_timer = FPS * INVINCIBILITY
                    hit_count += 1
                if explosion.crater_created and not explosion.finished:
                    if not giant_asteroid_landed and explosion != giant_explosion:
                        craters.append(Crater(explosion.rect.center, explosion.scale))
                    explosion.crater_created = False
                if explosion.finished:
                    explosions.remove(explosion)
                    if explosion == giant_explosion:
                        giant_explosion = None

            for crater in craters[:]:
                if crater.is_expired():
                    craters.remove(crater)

            current_time = pygame.time.get_ticks() - total_pause_time
            if current_time - last_difficulty_increase_time > DIFFICULTY_INCREASE_INTERVAL:
                last_difficulty_increase_time = current_time
                asteroid_speed += ASTEROID_SPEED_INCREMENT
                asteroid_spawn_delay = max(50, asteroid_spawn_delay - ASTEROID_SPAWN_DELAY_DECREMENT)
                crater_life = max(5, crater_life - CRATER_LIFE_DECREMENT)
                pygame.time.set_timer(pygame.USEREVENT, asteroid_spawn_delay)

        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        if giant_asteroid_landed:
            surface.fill((255, 255, 255))
        else:
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
            if blood_screen_timer > 0 and not paused:
                blood_screen_timer -= 1
                surface.blit(pygame.transform.scale(blood_screen, (SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0))
            if paused:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 128))
                surface.blit(overlay, (0, 0))
                draw_text(surface, "PAUSE", font, (255, 255, 255), SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20)
                draw_text(surface, "press ESC to play", font, (255, 255, 255), SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20)
            elapsed_time = pygame.time.get_ticks() - start_time - (total_pause_time if not paused else total_pause_time + (pygame.time.get_ticks() - pause_start_time))
            time_text = font.render(f"Čas: {format_time(elapsed_time)}", True, (255, 255, 255))
            surface.blit(time_text, (10, 10))
            for i in range(hit_count):
                surface.blit(skull_image, (10 + i * 50, 40))

        shake_x, shake_y = apply_shake_effect(SHAKE_INTENSITY) if not paused and not giant_asteroid_landed else (0, 0)
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
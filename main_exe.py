import os
import sys
import pygame
import random
import time

# Konstanty
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 1000
FPS = 60

SHAKE_INTENSITY = 1  # Konstantní intenzita otřesů

CRATERLIVE = 15  # Doba života kráteru v sekundách

ASTEROID_SPAWN_DELAY = 400
ASTEROID_SPEED = 25
CHARACTER_SPEED = 7
RANDOM_MIN = 0.8
RANDOM_MAX = 2.5

INVINCIBILITY = 1

DORAZ = 23
ROZMEZI_Y = SCREEN_HEIGHT // DORAZ
ROZMEZI_X = SCREEN_HEIGHT // DORAZ

# Parametry zvyšování obtížnosti
DIFFICULTY_INCREASE_INTERVAL = 700  # Interval zvyšování obtížnosti v milisekundách
ASTEROID_SPEED_INCREMENT = 0.1  # Zvýšení rychlosti asteroidů
ASTEROID_SPAWN_DELAY_DECREMENT = 5  # Snížení zpoždění mezi generováním asteroidů
CRATER_LIFE_DECREMENT = 1  # Snížení délky života kráteru
# Inicializace Pygame

def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Crater:
    def __init__(self, position, scale):
        self.image = pygame.image.load(resource_path('media/crater.png')).convert_alpha()
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
    
class Explosion:
    def __init__(self, position, scale):
        self.scale = scale
        self.sprite_sheet = pygame.image.load(resource_path('media/explosion.png')).convert_alpha()
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
            
class Target:
    def __init__(self, x, y, scale):
        self.image = pygame.image.load(resource_path('media/target.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, ((self.image.get_width() // 5) * scale, (self.image.get_height() // 5) * scale))
        self.rect = self.image.get_rect(center=(x, y))

    def draw(self, surface):
        offset_rect = self.rect.copy()
        offset_rect.x -= self.rect.width * 0.0  # Posun vlevo o čtvrtinu šířky
        surface.blit(self.image, offset_rect)
        
class Asteroid:
    def __init__(self):
        self.scale = random.uniform(RANDOM_MIN, RANDOM_MAX)  # Náhodné zvětšení asteroidu
        self.sprite_sheet = pygame.image.load(resource_path('media/asteroid.png')).convert_alpha()
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
          
class Character:
    def __init__(self):
        self.sprite_sheet = pygame.image.load(resource_path('media/sprite-person.png')).convert_alpha()
        self.frame_width = 64
        self.frame_height = 64
        self.directions = ["down", "left", "right", "up"]
        self.frames = self.load_frames()

        self.image = self.frames["down"][0]
        self.rect = self.image.get_rect()
        self.rect.center = (400, 300)
        self.lives = 5  # Počet životů inicializován na 5
        self.current_direction = "down"
        self.animation_index = 0
        self.animation_speed = 0.1
        self.animation_counter = 0
        self.invincible = False
        self.invincible_timer = 0
        self.speed = CHARACTER_SPEED

    def load_frames(self):
        frames = {direction: [] for direction in self.directions}
        for i, direction in enumerate(self.directions):
            for j in range(4):
                frame = self.sprite_sheet.subsurface(
                    pygame.Rect(j * self.frame_width, i * self.frame_height, self.frame_width, self.frame_height)
                )
                frames[direction].append(frame)
        return frames

    def update(self):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        direction = None

        if keys[pygame.K_LEFT]:
            dx = -self.speed
            direction = "left"
        if keys[pygame.K_RIGHT]:
            dx = self.speed
            direction = "right"
        if keys[pygame.K_UP]:
            dy = -self.speed
            direction = "up"
        if keys[pygame.K_DOWN]:
            dy = self.speed
            direction = "down"

        self.rect.x += dx
        self.rect.y += dy

        # Kontrola hranic okna
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

        if direction:
            self.current_direction = direction
            self.animate()
        else:
            self.animation_index = 0
            self.image = self.frames[self.current_direction][0]

        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False


    def animate(self):
        self.animation_counter += self.animation_speed
        if self.animation_counter >= 1:
            self.animation_counter = 0
            self.animation_index = (self.animation_index + 1) % len(self.frames[self.current_direction])
            self.image = self.frames[self.current_direction][self.animation_index]

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        #pygame.draw.rect(screen, (255, 255, 255), self.rect, 1)  # Vykreslení hitboxu postavy

        # Vykreslení hitboxu pro kontrolu
       #character_hitbox = pygame.Rect(self.rect.x + self.rect.width // 6, self.rect.y + self.rect.height // 6, self.rect.width * 2 // 3, self.rect.height * 2 // 3)
       # pygame.draw.rect(screen, (0, 255, 0), character_hitbox, 1)  # Vykreslení hitboxu postavy

    def hit(self):
        if not self.invincible:
            self.lives -= 1
            self.invincible = True
            self.invincible_timer = FPS * INVINCIBILITY  # 2 sekundy při 60 FPS

pygame.init()

# Nastavení obrazovky
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("DOOM'S DAY")

# Načtení a škálování pozadí
background = pygame.image.load(resource_path('media/background.png'))
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
blood_screen = pygame.image.load(resource_path('media/blood_screen.png')).convert_alpha()
skull_image = pygame.image.load(resource_path('media/skull.png')).convert_alpha()
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
    background = pygame.image.load(resource_path('media/game.png'))
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

    while True:
        screen.blit(background, (0, 0))
        draw_text(screen, "Doom's day", font, (255, 255, 255), SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
        draw_text(screen, "Press ENTER to PLAY", font, (255, 255, 255), SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        draw_text(screen, "Press ESC to EXIT", font, (255, 255, 255), SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

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
                sys.exit()
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
            running = False 

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
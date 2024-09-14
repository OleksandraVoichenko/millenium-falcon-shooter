from os.path import join
from random import randint, uniform
import pygame
from patsy.state import center

SCORES_FILE = './scores.txt'

# pygame setup
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT)) # create display
pygame.display.set_caption("Millennium Falcon: Grand Escape")
running = True
gameover = False
clock = pygame.time.Clock()

# import images
star_surf = pygame.image.load(join('images', 'star.png')).convert_alpha()
star_surf = pygame.transform.scale(star_surf, (500, 500))
starfighter_surf = pygame.image.load(join('images', 'starfighter.png')).convert_alpha()
starfighter_surf = pygame.transform.scale(starfighter_surf, (150, 150))
laser_surf = pygame.image.load(join('images', 'laser.png')).convert_alpha()
font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 30)
explosion_frames = [pygame.image.load(join('images', 'explosion', f'{i}.png')).convert_alpha() for i in range(21)]

# sound & visuals
laser_sound = pygame.mixer.Sound(join('audio', 'laser.wav'))
explosion_sound = pygame.mixer.Sound(join('audio', 'explosion.wav'))
game_music = pygame.mixer.Sound(join('audio', 'game_music.wav'))
game_music.set_volume(0.5)
game_music.play()

# classes
class Shooter(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(join('images', 'millennium-falcon.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (110, 140))
        self.rect = self.image.get_frect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
        self.speed = 300
        self.dir = pygame.math.Vector2()

        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown = 1000

        self.mask = pygame.mask.from_surface(self.image)

    def laser_timer(self):
        if not self.can_shoot:
            curr_time = pygame.time.get_ticks()
            if curr_time - self.laser_shoot_time >= self.cooldown:
                self.can_shoot = True

    def update(self, delta_t):
        keys = pygame.key.get_pressed()
        self.dir.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.dir.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.dir = self.dir.normalize() if self.dir else self.dir
        self.rect.center += self.dir * self.speed * delta_t

        if self.rect.right >= WINDOW_WIDTH:
            self.rect.right = WINDOW_WIDTH
        if self.rect.left <= 0:
            self.rect.left = 0
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= WINDOW_HEIGHT:
            self.rect.bottom = WINDOW_HEIGHT

        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser(laser_surf, self.rect.midtop, (all_sprites, laser_sprites))
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            laser_sound.play()

        self.laser_timer()

class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.image = surf
        self.pos = [randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT)]
        self.rect = self.image.get_frect(center=(self.pos[0], self.pos[1]))

class Starfighter(pygame.sprite.Sprite):
    def __init__(self, groups, surf, speed_multiplier=1):
        super().__init__(groups)
        self.image = surf
        self.pos = [randint(10, WINDOW_WIDTH-10), -10]
        self.rect = self.image.get_frect(center=(self.pos[0], self.pos[1]))
        self.start_time = pygame.time.get_ticks()
        self.direction = pygame.Vector2(uniform(-0.5, 0.5), 1)
        self.speed = randint(300, 400) * speed_multiplier
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, delta_t):
        self.rect.center += self.direction * self.speed * delta_t
        if self.rect.top >= WINDOW_HEIGHT:
            self.kill()

class Laser(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom=pos)

    def update(self, delta_t):
        self.rect.centery -= 400 * delta_t
        if self.rect.bottom < -5:
            self.kill()

class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center=pos)

    def update(self, delta_t):
        self.frame_index += 20 * delta_t
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index) % len(self.frames)]
        else:
            self.kill()


# functions
def collisions():
    global running, gameover
    collision_sprites = pygame.sprite.spritecollide(shooter, starfighter_sprites, False, pygame.sprite.collide_mask)
    if collision_sprites:
        print("YOU LOSE!")
        save_score(score)
        gameover = True


    for laser in laser_sprites:
        collided_sprites = pygame.sprite.spritecollide(laser, starfighter_sprites, True, pygame.sprite.collide_mask)
        if collided_sprites:
            laser.kill()
            AnimatedExplosion(explosion_frames, laser.rect.midtop, all_sprites)
            explosion_sound.play()


# Initialize start_time
start_time = pygame.time.get_ticks()

# Function to display the score
def display_score(curr_time):
    # Calculate the elapsed time based on the difference from start_time
    elapsed_time = curr_time - start_time
    total_seconds = elapsed_time // 1000
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    text_surf = font.render(f'{minutes:02}:{seconds:02}', True, (240, 240, 240))
    text_rect = text_surf.get_frect(midbottom=(WINDOW_WIDTH / 2, WINDOW_HEIGHT - 50))
    screen.blit(text_surf, text_rect)
    pygame.draw.rect(screen, (240, 240, 240), text_rect.inflate(20, 20).move(0, -8), 5, 10)
    return f'{minutes:02}:{seconds:02}'

def save_score(score_to_save):
    with open(SCORES_FILE, 'a') as file:
        file.write(f'{score_to_save}\n')

# Function to draw buttons and return their Rect for click detection
def draw_buttons():
    global score
    score_text_surf = font.render(f'SCORE: {score}', True, (240, 240, 240))
    score_text_rect = score_text_surf.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
    screen.blit(score_text_surf, score_text_rect)

    restart_b_surf = font.render('RESTART', True, (240, 240, 240))
    restart_b_rect = restart_b_surf.get_frect(center=(WINDOW_WIDTH / 2.7, WINDOW_HEIGHT - 250))
    screen.blit(restart_b_surf, restart_b_rect)
    pygame.draw.rect(screen, (240, 240, 240), restart_b_rect.inflate(20, 20).move(0, -8), 5, 10)

    quit_b_surf = font.render('QUIT', True, (240, 240, 240))
    quit_b_rect = quit_b_surf.get_frect(center=(WINDOW_WIDTH / 1.6, WINDOW_HEIGHT - 250))
    screen.blit(quit_b_surf, quit_b_rect)
    pygame.draw.rect(screen, (240, 240, 240), quit_b_rect.inflate(20, 20).move(0, -8), 5, 10)

    return restart_b_rect, quit_b_rect

# Restart function to reset game variables
def restart_game():
    global shooter, score, gameover, last_speed_increase, starfighter_speed_multiplier, current_time, start_time
    shooter.rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)  # Move shooter to the center
    score = 0  # Reset score
    current_time = 0
    start_time = pygame.time.get_ticks()  # Reset start_time to current time
    gameover = False  # Set gameover to False
    last_speed_increase = pygame.time.get_ticks()  # Reset the timer for speed increase
    starfighter_speed_multiplier = 1  # Reset speed multiplier
    # Optionally, clear out existing starfighters and lasers
    for sprite in starfighter_sprites:
        sprite.kill()
    for sprite in laser_sprites:
        sprite.kill()

# Function to show game over screen
def game_over_screen():
    screen.fill('#010210')
    restart_button_rect, quit_button_rect = draw_buttons()
    pygame.display.update()

    # Event loop to handle button clicks
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                # Check if restart button was clicked
                if restart_button_rect.collidepoint(mouse_pos):
                    restart_game()
                    return  # Exit the game over loop and restart the game

                # Check if quit button was clicked
                if quit_button_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    exit()

# add sprites
all_sprites = pygame.sprite.Group()
for i in range(20):
    star = Star(all_sprites, star_surf)
starfighter_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()
shooter = Shooter(all_sprites)

starfighter_event = pygame.event.custom_type()
pygame.time.set_timer(starfighter_event, 300)

starfighter_speed_multiplier = 1
increase_speed_time = 30000
last_speed_increase = pygame.time.get_ticks()
score = 0


while running:
    dt = clock.tick() / 1000
    current_time = pygame.time.get_ticks()

    # speed up the starfighters
    if current_time - last_speed_increase >= increase_speed_time:
        starfighter_speed_multiplier += 0.1
        last_speed_increase = current_time

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == starfighter_event and not gameover:
            Starfighter((all_sprites, starfighter_sprites), starfighter_surf, starfighter_speed_multiplier)
        if event.type == pygame.KEYDOWN:
            if gameover and event.key == pygame.K_r:
                restart_game()

    # Game over screen
    if gameover:
        game_over_screen()
    else:
        # Normal game loop
        screen.fill('#010210')
        all_sprites.update(dt)
        collisions()
        score = display_score(current_time)
        all_sprites.draw(screen)
        pygame.display.update()

pygame.quit()

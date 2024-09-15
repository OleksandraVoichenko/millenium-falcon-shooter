from os.path import join
from random import randint, uniform
import pygame

from Scoreboard import Scoreboard

# constants
SCORES_FILE = './scores.txt'
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
BACKGROUND_COLOR = '#010210'
TEXT_COLOR = (240, 240, 240)
LEVEL_UP_TIME = 30000
FALCON_SPEED = 300
LASER_SPEED = 400


# pygame setup
pygame.init()
pygame.display.set_caption("Millennium Falcon: Grand Escape")
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()
game_over = False
running = True


# import assets
star_surf = pygame.transform.scale(pygame.image.load(join('images', 'star.png')).convert_alpha(), (500, 500))
enemy_surf = pygame.transform.scale(pygame.image.load(join('images', 'starfighter.png')).convert_alpha(), (150, 150))
laser_surf = pygame.image.load(join('images', 'laser.png')).convert_alpha()

explosion_frames = [pygame.image.load(join('images', 'explosion', f'{i}.png')).convert_alpha() for i in range(21)]
explosion_sound = pygame.mixer.Sound(join('audio', 'flying.wav'))
font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 30)
game_music = pygame.mixer.Sound(join('audio', 'star-wars.mp3'))
game_over_sound = pygame.mixer.Sound(join('audio', 'chewy.wav'))
laser_sound = pygame.mixer.Sound(join('audio', 'rifle.wav'))
score_board_sound = pygame.mixer.Sound(join('audio', 'vader.wav'))
reset_txt_sound = pygame.mixer.Sound(join('audio', 'as_u_wish.wav'))
game_music.set_volume(0.5)
game_music.play(loops=-1)


# sprite classes
class Falcon(pygame.sprite.Sprite):
    def __init__(self, groups):
        """Creates falcon model and initial logic of sprite"""
        super().__init__(groups)
        self.image = pygame.transform.scale(pygame.image.load(join('images', 'millennium-falcon.png')).convert_alpha(), (110, 140))
        self.rect = self.image.get_frect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
        self.dir = pygame.math.Vector2()
        self.speed = FALCON_SPEED
        self.laser_shoot_time = 0
        self.can_shoot = True
        self.cooldown = 1000
        self.mask = pygame.mask.from_surface(self.image)


    def laser_timer(self):
        """Sets the cooldown of laser"""
        if not self.can_shoot:
            curr_time = pygame.time.get_ticks()
            if curr_time - self.laser_shoot_time >= self.cooldown:
                self.can_shoot = True


    def update(self, delta_t):
        """Handles movement of sprite"""
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
        """Creates star sprites"""
        super().__init__(groups)
        self.image = surf
        self.pos = [randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT)]
        self.rect = self.image.get_frect(center=(self.pos[0], self.pos[1]))

class Enemy(pygame.sprite.Sprite):
    def __init__(self, groups, surf, speed_multiplier=1):
        """Creates starfighter (enemy) of the game"""
        super().__init__(groups)
        self.image = surf
        self.pos = [randint(10, WINDOW_WIDTH-10), -10]
        self.rect = self.image.get_frect(center=(self.pos[0], self.pos[1]))
        self.start_time = pygame.time.get_ticks()
        self.direction = pygame.Vector2(uniform(-0.5, 0.5), 1)
        self.speed = randint(300, 400) * speed_multiplier
        self.mask = pygame.mask.from_surface(self.image)


    def update(self, delta_t):
        """Updates movement logic of starfighters"""
        self.rect.center += self.direction * self.speed * delta_t
        if self.rect.top >= WINDOW_HEIGHT:
            self.kill()

class Laser(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        """Creates laser"""
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom=pos)


    def update(self, delta_t):
        """Creates speed and movement logic of lasers"""
        self.rect.centery -= LASER_SPEED * delta_t
        if self.rect.bottom < -5:
            self.kill()

class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        """Creates animation effects"""
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center=pos)


    def update(self, delta_t):
        """Updates movement (occurrence) logic of explosions"""
        self.frame_index += 20 * delta_t
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index) % len(self.frames)]
        else:
            self.kill()


# functions
def collisions():
    """Checks collision between sprites"""
    global running, game_over
    falcon_col_sprites = pygame.sprite.spritecollide(falcon, enemy_sprites, False, pygame.sprite.collide_mask)
    if falcon_col_sprites:
        game_music.stop()
        game_over_sound.play()
        save_score(score)
        game_over = True

    for laser in laser_sprites:
        laser_col_sprites = pygame.sprite.spritecollide(laser, enemy_sprites, True, pygame.sprite.collide_mask)
        if laser_col_sprites:
            laser.kill()
            AnimatedExplosion(explosion_frames, laser.rect.midtop, all_sprites)
            explosion_sound.play()


# Initialize start_time
game_start_time = pygame.time.get_ticks()

def display_score(curr_game_time):
    """Displays score following custom convention"""
    elapsed_time = curr_game_time - game_start_time
    total_seconds = elapsed_time // 1000
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    text_surf = font.render(f'{minutes:02}:{seconds:02}', True, TEXT_COLOR)
    text_rect = text_surf.get_frect(midbottom=(WINDOW_WIDTH / 2, WINDOW_HEIGHT - 50))
    screen.blit(text_surf, text_rect)
    pygame.draw.rect(screen, TEXT_COLOR, text_rect.inflate(20, 20).move(0, -8), 5, 10)
    return f'{minutes:02}:{seconds:02}'


def save_score(score_to_save):
    """Saves final scores to the .txt file"""
    with open(SCORES_FILE, 'a') as file:
        file.write(f'{score_to_save}\n')


def draw_buttons():
    """Draws buttons on restart menu and returns their Rect for click detection"""
    global score
    score_txt_surf = font.render(f'SCORE: {score}', True, TEXT_COLOR)
    score_txt_rect = score_txt_surf.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
    screen.blit(score_txt_surf, score_txt_rect)

    restart_b_surf = font.render('RESTART', True, TEXT_COLOR)
    restart_b_rect = restart_b_surf.get_frect(center=(WINDOW_WIDTH / 2.7, WINDOW_HEIGHT - 250))
    screen.blit(restart_b_surf, restart_b_rect)
    pygame.draw.rect(screen, TEXT_COLOR, restart_b_rect.inflate(20, 20).move(0, -8), 5, 10)

    quit_b_surf = font.render('QUIT', True, TEXT_COLOR)
    quit_b_rect = quit_b_surf.get_frect(center=(WINDOW_WIDTH / 1.6, WINDOW_HEIGHT - 250))
    screen.blit(quit_b_surf, quit_b_rect)
    pygame.draw.rect(screen, TEXT_COLOR, quit_b_rect.inflate(20, 20).move(0, -8), 5, 10)

    scoreboard_b_surf = font.render('SCOREBOARD', True, TEXT_COLOR)
    scoreboard_b_rect = scoreboard_b_surf.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT - 150))
    screen.blit(scoreboard_b_surf, scoreboard_b_rect)
    pygame.draw.rect(screen, TEXT_COLOR, scoreboard_b_rect.inflate(20, 20).move(0, -8), 5, 10)

    return restart_b_rect, quit_b_rect, scoreboard_b_rect


def restart_game():
    """Resets game variables after restart"""
    global falcon, score, game_over, last_speed_increase, enemy_speed_level, played_time, game_start_time
    falcon.rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
    game_start_time = pygame.time.get_ticks()
    played_time = 0
    score = 0
    game_over = False
    last_speed_increase = pygame.time.get_ticks()
    enemy_speed_level = 1
    for sprite in enemy_sprites:
        sprite.kill()
    for sprite in laser_sprites:
        sprite.kill()
    game_music.play(loops=-1)


def scoreboard_screen():
    """Creates score board and tracks clicks"""
    scoreboard = Scoreboard()
    running_scoreboard = True
    score_board_sound.play(loops=-1)
    while running_scoreboard:
        for score_event in pygame.event.get():
            if score_event.type == pygame.QUIT:
                pygame.quit()
                exit()

        screen.fill(BACKGROUND_COLOR)
        back_button_rect, reset_button_rect = scoreboard.draw_scoreboard(screen, font)

        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()
        if back_button_rect.collidepoint(mouse_pos) and mouse_click[0]:
            score_board_sound.stop()
            running_scoreboard = False
        if reset_button_rect.collidepoint(mouse_pos) and mouse_click[0]:
            reset_txt_sound.play()
            open(SCORES_FILE, "w").close()

        pygame.display.flip()


def game_over_screen():
    """Shows game over screen with buttons and detects clicks"""
    screen.fill(BACKGROUND_COLOR)
    restart_b_rect, quit_b_rect, scoreboard_b_rect = draw_buttons()
    pygame.display.update()

    while True:
        for go_event in pygame.event.get():
            if go_event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if go_event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if restart_b_rect.collidepoint(mouse_pos):
                    restart_game()
                    return
                if quit_b_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    exit()
                if scoreboard_b_rect.collidepoint(mouse_pos):
                    scoreboard_screen()
                    return


# add sprites
all_sprites = pygame.sprite.Group()
enemy_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()

for i in range(20):
    star = Star(all_sprites, star_surf)
falcon = Falcon(all_sprites)


# logic to create and speed up starfighters
starfighter_event = pygame.event.custom_type()
pygame.time.set_timer(starfighter_event, 300)
last_speed_increase = pygame.time.get_ticks()
enemy_speed_level = 1


# main loop
score = 0
scoreboard = Scoreboard()
while running:
    dt = clock.tick() / 1000
    played_time = pygame.time.get_ticks()

    if played_time - last_speed_increase >= LEVEL_UP_TIME:
        enemy_speed_level += 0.1
        last_speed_increase = played_time

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == starfighter_event and not game_over:
            Enemy((all_sprites, enemy_sprites), enemy_surf, enemy_speed_level)
        if event.type == pygame.KEYDOWN:
            if game_over and event.key == pygame.K_r:
                restart_game()

    if game_over:
        game_over_screen()
    else:
        screen.fill(BACKGROUND_COLOR)
        all_sprites.update(dt)
        collisions()
        score = display_score(played_time)
        all_sprites.draw(screen)
        pygame.display.update()


pygame.quit()

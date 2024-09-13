from os.path import join
from random import randint, uniform
import pygame

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
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown:
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

class Meteor(pygame.sprite.Sprite):
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
    global running
    collision_sprites = pygame.sprite.spritecollide(shooter, meteor_sprites, False, pygame.sprite.collide_mask)
    if collision_sprites:
        print("YOU LOSE!")
        running = False


    for laser in laser_sprites:
        collided_sprites = pygame.sprite.spritecollide(laser, meteor_sprites, True, pygame.sprite.collide_mask)
        if collided_sprites:
            laser.kill()
            AnimatedExplosion(explosion_frames, laser.rect.midtop, all_sprites)
            explosion_sound.play()

def display_score():
    curr_time = pygame.time.get_ticks()
    total_seconds = curr_time // 1000
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    text_surf = font.render(f'{minutes:02}:{seconds:02}', True, (240, 240, 240 ))
    text_rect = text_surf.get_frect(midbottom=(WINDOW_WIDTH / 2, WINDOW_HEIGHT - 50))
    screen.blit(text_surf, text_rect)
    pygame.draw.rect(screen, (240, 240, 240), text_rect.inflate(20, 20).move(0, -8), 5, 10)


# pygame setup
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT)) # create display
pygame.display.set_caption("Space Shooter")
running = True
clock = pygame.time.Clock()

# import images
star_surf = pygame.image.load(join('images', 'star.png')).convert_alpha()
star_surf = pygame.transform.scale(star_surf, (500, 500))
meteor_surf = pygame.image.load(join('images', 'starfighter.png')).convert_alpha()
meteor_surf = pygame.transform.scale(meteor_surf, (150, 150))
laser_surf = pygame.image.load(join('images', 'laser.png')).convert_alpha()
font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 30)
explosion_frames = [pygame.image.load(join('images', 'explosion', f'{i}.png')).convert_alpha() for i in range(21)]

# sound & visuals
laser_sound = pygame.mixer.Sound(join('audio', 'laser.wav'))
explosion_sound = pygame.mixer.Sound(join('audio', 'explosion.wav'))
game_music = pygame.mixer.Sound(join('audio', 'game_music.wav'))
game_music.set_volume(0.5)
game_music.play()


# add sprites
all_sprites = pygame.sprite.Group()
for i in range(20):
    star = Star(all_sprites, star_surf)
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()
shooter = Shooter(all_sprites)

meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 300)

meteor_speed_multiplier = 1
increase_speed_time = 30000
last_speed_increase = pygame.time.get_ticks()
while running:
    dt = clock.tick() / 1000
    current_time = pygame.time.get_ticks()

    if current_time - last_speed_increase >= increase_speed_time:
        meteor_speed_multiplier += 0.1
        last_speed_increase = current_time

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == meteor_event:
            Meteor((all_sprites, meteor_sprites), meteor_surf, meteor_speed_multiplier)

    screen.fill('#010210')

    all_sprites.update(dt)
    collisions()
    display_score()
    all_sprites.draw(screen)

    pygame.display.update()

pygame.quit()

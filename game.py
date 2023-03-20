import pygame
import math
from sys import exit
from random import randint, choice
from player import *


# Enemy
class Snail(pygame.sprite.Sprite): 
    def __init__(self, pos, group):
        super().__init__(group)
        snail_1 = pygame.image.load('graphics/snail/snail1.png').convert_alpha()
        snail_2 = pygame.image.load('graphics/snail/snail2.png').convert_alpha()
        snail_1_flipped = pygame.transform.flip(snail_1, True, False)
        snail_2_flipped = pygame.transform.flip(snail_2, True, False)

        self.frames = [snail_1, snail_2]
        self.frames_flipped = [snail_1_flipped, snail_2_flipped]
        self.animation_index = 0

        self.image = self.frames[self.animation_index]
        self.rect = self.image.get_rect(midbottom=pos)
        self.health = 70
        self.direction = -4

    def collision(self, bullets, obstacles):
        if pygame.sprite.groupcollide(bullets, obstacles, True, False):
            self.health -= 8

    def walk_animation(self, direction):
        self.animation_index += 0.1
        if self.animation_index >= 2: self.animation_index = 0
        if direction == 'right':
            self.image = self.frames[int(self.animation_index)]
        elif direction == 'left':
            self.image = self.frames_flipped[int(self.animation_index)]

    def movement(self, player):
        if self.rect.x - player.rect.x < -100:
            self.walk_animation('left')
            self.direction = 3.5
        elif self.rect.x - player.rect.x > 100:
            self.walk_animation('right')
            self.direction = -3.5
        self.rect.x += self.direction

    def destroy(self, sprite):
        if self.health <= 0:
            global snail_count
            snail_count -= 1
            enemy_list.remove(sprite)
            global kill_count
            kill_count += 1
            self.kill()


class Fly(pygame.sprite.Sprite):
    def __init__(self, pos, group):
        super().__init__(group)
        fly_1 = pygame.image.load('graphics/fly/fly1.png').convert_alpha()
        fly_2 = pygame.image.load('graphics/fly/fly2.png').convert_alpha()
        fly_1_flipped = pygame.transform.flip(fly_1, True, False)
        fly_2_flipped = pygame.transform.flip(fly_2, True, False)

        self.frames = [fly_1, fly_2]
        self.frames_flipped = [fly_1_flipped, fly_2_flipped]
        self.animation_idx = 0

        self.image = self.frames[self.animation_idx]
        self.rect = self.image.get_rect(midbottom=pos)
        self.health = 40
        self.direction = -4

        # Fly bullet
        self.bullet = pygame.image.load('graphics/02.png').convert_alpha()
        self.bullet_rect = self.bullet.get_rect(center=pos)

    def collision(self, bullets, obstacles):
        if pygame.sprite.groupcollide(bullets, obstacles, True, False):
            self.health -= 8

    def walk_animation(self, direction):
        self.animation_idx += 0.1
        if self.animation_idx >= 2: self.animation_idx = 0
        if direction == 'right':
            self.image = self.frames[int(self.animation_idx)]
        elif direction == 'left':
            self.image = self.frames_flipped[int(self.animation_idx)]

    def movement(self, player):
        if self.rect.x - player.rect.x < -100:
            self.walk_animation('left')
            self.direction = 4
        elif self.rect.x - player.rect.x > 100:
            self.walk_animation('right')
            self.direction = -4
        self.rect.x += self.direction

    def shoot(self, player):
        fly_bullet = FlyBullet(self.rect.center, camera_group, player, self.rect)
        fly_bullet_group.add(fly_bullet)

    def flight_height(self):
        self.rect.y += randint(-12, 12)
        if self.rect.bottom >= 455:
            self.rect.bottom = 455
        if self.rect.top <= 205:
            self.rect.top = 205

    def destroy(self, sprite):
        if self.health <= 0:
            global fly_counter
            fly_counter -= 1
            enemy_list.remove(sprite)
            global kill_count
            kill_count += 1
            self.kill()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, group, target, start_rect):
        super().__init__(group)
        self.image = pygame.image.load('graphics/01.png').convert_alpha()
        self.rect = self.image.get_rect(center=pos)

        self.original = self.image
        self.flipped = pygame.transform.flip(self.image, True, False)

        self.target = pygame.mouse.get_pos()
        self.start = pygame.math.Vector2(start_rect.x, start_rect.y)
        self.camera_offset = camera_group.get_offset()

    def shoot(self):
        if self.target[0] + self.camera_offset < self.start.x:
            self.image = self.flipped
            self.rect.x -= 10
        else:
            self.image = self.original
            self.rect.x += 10

    def destroy(self, bool):
        if abs(self.rect.x - self.start.x) > 700 or bool:
            print('destroyed')
            self.kill()

    def update(self):
        self.shoot()
        self.destroy(False)


class FlyBullet(pygame.sprite.Sprite):
    def __init__(self, pos, group, target, start_rect):
        super().__init__(group)
        self.image = pygame.image.load('graphics/02.png').convert_alpha()
        self.rect = self.image.get_rect(center=pos)

        self.target = target
        self.start = pygame.math.Vector2(start_rect.x, start_rect.y)

    def shoot(self):
        dx = self.target.x - self.start.x
        dy = self.target.y - self.start.y
        angle = math.atan2(dy, dx)
        self.rect.x += math.cos(angle) * 8
        self.rect.y += math.sin(angle) * 8

    def destroy(self):
        if abs(self.rect.x - self.start.x) > 1100 or abs(self.rect.y - self.start.y) > 1000:
            self.kill()

    def update(self):
        self.shoot()
        self.destroy()


class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        # Background
        self.test_bg = pygame.image.load('graphics/new_bg.png').convert_alpha()
        self.test_rect = self.test_bg.get_rect(topleft=(-112, 0))

        self.ground = pygame.image.load('graphics/new_ground.png').convert_alpha()
        self.ground_rect = self.ground.get_rect(topleft=(-112, 500))

        self.display_surf = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()

        # Box camera
        self.camera_borders = {'left' : 300, 'right' : 250, 'top' : 300, 'bottom' : 100}
        l = self.camera_borders['left']
        t = self.camera_borders['top']
        w = self.display_surf.get_size()[0] - self.camera_borders['right'] - self.camera_borders['left']
        h = self.display_surf.get_size()[1] - self.camera_borders['bottom'] - self.camera_borders['top']
        self.camera_rect = pygame.Rect(l,t,w,h)

    # Camera movement
    def box_camera(self, target):
        if target.rect.left < self.camera_rect.left:
            self.camera_rect.left = target.rect.left
        if target.rect.right > self.camera_rect.right:
            self.camera_rect.right = target.rect.right

        self.offset.x = self.camera_rect.left - self.camera_borders['left']

    def get_offset(self):
        return self.offset.x

    # Display func
    def custom_draw(self, player):
        self.box_camera(player)
        # Background
        bg_offset = self.test_rect.topleft - self.offset
        self.display_surf.blit(self.test_bg, bg_offset)
        self.display_surf.blit(self.ground, bg_offset + (0, 500))

        # Sprites
        for sprite in self.sprites():
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surf.blit(sprite.image, offset_pos)


def display_kill_count():
    font_style = pygame.font.Font('font/Pixeltype.ttf', 50)
    count_surf = font_style.render(f'Kill Count: {kill_count}',False,(125, 209, 205))
    count_rect = count_surf.get_rect(topleft=(800, 30))
    pygame.display.get_surface().blit(count_surf, count_rect)


def end_game():
    pygame.quit()
    exit()


def game_reset():
    global enemy_list
    player.player_reset()
    for sprite in enemy_list:
        sprite.kill()
    enemy_group.empty()
    fly_bullet_group.empty()
    bullet_group.empty()
    enemy_list = []


# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((1000, 650))
pygame.display.set_caption('Deep Into The Wilds')
clock = pygame.time.Clock()
font_style = pygame.font.Font('font/Pixeltype.ttf', 50)
game_end = True

# Music
game_music = pygame.mixer.Sound('audio/game_start_music.mp3')
game_music.set_volume(0.3)
intro_music = pygame.mixer.Sound('audio/Intro_screen_music.mp3')
gun_sound = pygame.mixer.Sound('audio/gun_shot.wav')
jump_sound = pygame.mixer.Sound('audio/audio_jump.mp3')
jump_sound.set_volume(0.4)

# Intro screen
background = pygame.image.load('graphics/background/forest.png').convert_alpha()
background = pygame.transform.rotozoom(background, 0, 1.6)
background_rect = background.get_rect(center=(500, 325))

game_title = font_style.render('Deep Into The Wilds', False, (77, 126, 191))
game_title = pygame.transform.rotozoom(game_title, 0, 2)
game_title_rect = game_title.get_rect(center=(500,150))

# Play button
play = font_style.render('Play', False, (77, 126, 191))
play = pygame.transform.rotozoom(play, 0, 1.35)
play_rect = play.get_rect(center=(500,325))

# Instructions
ins = font_style.render('Instructions', False, (77, 126, 191))
ins = pygame.transform.rotozoom(ins, 0, 1.35)
ins_rect = ins.get_rect(center=(500,500))

ins1 = font_style.render('*  Press  SPACE / RIGHT  CLICK  to  JUMP', False, (200, 221, 250))
ins2 = font_style.render('*  Position  mouse  and  CLICK  to  SHOOT', False, (200, 221, 250))
ins3 = font_style.render('*  KILL  as  much  enemy  to  earn  POINTS', False, (200, 221, 250))
ins1_rect = ins1.get_rect(topleft=(200, 250))
ins2_rect = ins2.get_rect(topleft=(200, 325))
ins3_rect = ins3.get_rect(topleft=(200, 400))

# Back button
back = font_style.render('BACK', False, (77, 126, 191))
back_rect = back.get_rect(center=(500, 500))
ins_bool = False

# Replay
replay = font_style.render('PLAY AGAIN', False, (77, 126, 191))
replay_rect = replay.get_rect(center=(500, 500))

# Button list
button_list = ['play', 'ins']

# Camera
camera_group = CameraGroup()

# Player
player = Player((70, 500), camera_group)
player_group = pygame.sprite.GroupSingle()
player_group.add(player)

# Enemy
enemy_group = pygame.sprite.Group()
enemy_list = []

# Counters
snail_count = 0
fly_counter = 0

snail_limit = 2
fly_limit = 1

kill_count = 0

# Bullet
bullet_group = pygame.sprite.Group()
fly_bullet_group = pygame.sprite.Group()

# User events
snail_generate = 3000
fly_generate = 6000

snail_timer = pygame.USEREVENT + 1
pygame.time.set_timer(snail_timer, snail_generate)

fly_timer = pygame.USEREVENT + 2
pygame.time.set_timer(fly_timer, fly_generate)

fly_height_timer = pygame.USEREVENT + 3
pygame.time.set_timer(fly_height_timer, 200)

fly_shoot_timer = pygame.USEREVENT + 4
pygame.time.set_timer(fly_shoot_timer, 3000)

next_level = pygame.USEREVENT + 5
pygame.time.set_timer(next_level, 20000)

while True:
    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            end_game()

        if not game_end:
            if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 3) or pygame.key.get_pressed()[pygame.K_SPACE]:
                pygame.mixer.Channel(1).play(jump_sound)
                player.jump()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.math.Vector2(pygame.mouse.get_pos())
                player_rect = player.player_rect()
                bullet = Bullet((player_rect.right + 1, player_rect.centery + 15), camera_group, mouse_pos, player_rect)
                bullet_group.add(bullet)
                pygame.mixer.Channel(0).play(gun_sound)

            if event.type == snail_timer and snail_count < snail_limit:
                x = choice([(1000, 1500), (-1500, -1000)])
                snail = Snail((randint(player.player_rect().x + x[0], player.player_rect().x + x[1]), 500), camera_group)
                enemy_group.add(snail)
                enemy_list.append(snail)
                snail_count += 1

            if event.type == fly_timer and fly_counter < fly_limit:
                x = choice([(1000, 2000), (-2000, -1000)])
                fly = Fly((randint(player.player_rect().x + x[0], player.player_rect().x + x[1]), 300), camera_group)
                enemy_group.add(fly)
                enemy_list.append(fly)
                fly_counter += 1

            if event.type == fly_height_timer and fly_counter > 0:
                fly.flight_height()
            if event.type == fly_shoot_timer and fly_counter > 0:
                fly.shoot(player.player_rect())

            if event.type == next_level or kill_count % 5 == 0:
                fly_limit += 1
                snail_limit += 2
        else:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_rect.collidepoint(event.pos) and 'play' in button_list:
                    game_end = False
                    button_list = ['replay']
                elif replay_rect.collidepoint(event.pos) and 'replay' in button_list:
                    game_end = False
                    kill_count = 0
                elif ins_rect.collidepoint(event.pos) and 'ins' in button_list:
                    game_end = True
                    ins_bool = True
                    button_list = ['back']
                elif back_rect.collidepoint(event.pos) and 'back' in button_list:
                    game_end = True
                    ins_bool = False
                    button_list = ['play', 'ins']

    if not game_end and not ins_bool:
        intro_music.stop()
        game_music.play()
        # Camera
        camera_group.update()
        camera_group.custom_draw(player)
        player.display_health()
        display_kill_count()

        # Music
        game_music.play()

        # Collision
        for enemy in enemy_list:
            enemy.collision(bullet_group, enemy_group)
            enemy.destroy(enemy)

        # Collision with player
        player.player_collision(player_group.sprite, enemy_group, False)
        player.player_collision(player_group.sprite, fly_bullet_group, True)
        pygame.sprite.groupcollide(bullet_group, fly_bullet_group, True, True)

        for enemy in enemy_list:
            enemy.movement(player)

        # game end
        game_end = player.dead()
    else:
        # Reset Values
        game_reset()

        # Music
        game_music.stop()
        intro_music.play()

        # Background
        screen.blit(background, background_rect)

        if not ins_bool:
            if kill_count:
                # Dead Font
                dead = font_style.render(f'YOU DIED!', False, (200, 221, 250))
                dead = pygame.transform.rotozoom(dead, 0, 2)
                dead_rect = dead.get_rect(center=(500, 250))
                screen.blit(dead, dead_rect)

                # Kill count font
                kills = font_style.render(f'POINTS : {kill_count}', False, (200, 221, 250))
                kills_rect = kills.get_rect(center=(500, 375))
                screen.blit(kills, kills_rect)

                # Replay button
                pygame.draw.rect(screen, (200, 221, 250), pygame.transform.rotozoom(replay, 0, 1.4).get_rect(center=(500, 500)), border_radius=5)
                screen.blit(replay, replay_rect)
            else:
                screen.blit(game_title, game_title_rect)
                pygame.draw.rect(screen, (200, 221, 250), pygame.transform.rotozoom(play, 0, 1.4).get_rect(center=(500, 325)), border_radius=5)
                screen.blit(play, play_rect)
                pygame.draw.rect(screen, (200, 221, 250), pygame.transform.rotozoom(ins, 0, 1.3).get_rect(center=(500, 500)), border_radius=5)
                screen.blit(ins, ins_rect)
        # Instruction screen
        else:
            ins_title = pygame.transform.rotozoom(ins, 0, 2)
            ins_title_rect = ins_title.get_rect(center=(500, 100))
            screen.blit(ins_title, ins_title_rect)
            screen.blit(ins1, ins1_rect)
            screen.blit(ins2, ins2_rect)
            screen.blit(ins3, ins3_rect)

            pygame.draw.rect(screen, (200, 221, 250), pygame.transform.rotozoom(back, 0, 1.3).get_rect(center=(500, 500)), border_radius=5)
            screen.blit(back, back_rect)

    pygame.display.update()
    clock.tick(60)

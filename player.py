import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group):
        super().__init__(group)
        player_walk_1 = pygame.image.load('graphics/Player/player_walk_1.png').convert_alpha()
        player_walk_2 = pygame.image.load('graphics/Player/player_walk_2.png').convert_alpha()
        player_walk_1_flipped = pygame.transform.flip(player_walk_1, True, False)
        player_walk_2_flipped = pygame.transform.flip(player_walk_2, True, False)

        self.player_stand = pygame.image.load('graphics/Player/player_stand.png').convert_alpha()
        self.player_stand_flipped = pygame.transform.flip(self.player_stand, True, False)
        self.player_jump = pygame.image.load('graphics/Player/jump.png').convert_alpha()

        self.walk_animation_list = [player_walk_1, player_walk_2]
        self.walk_animation_list_flipped = [player_walk_1_flipped, player_walk_2_flipped]
        self.animation_idx = 0

        self.image = self.player_stand
        self.rect = self.image.get_rect(midbottom=pos)
        self.gravity = 0
        self.health = 100

    def walk_animation(self, direction):
        self.animation_idx += 0.1
        if self.animation_idx >= 2: self.animation_idx = 0
        if direction == 'right' and self.rect.bottom >= 500:
            self.image = self.walk_animation_list[int(self.animation_idx)]
        elif direction == 'left' and self.rect.bottom >= 500:
            self.image = self.walk_animation_list_flipped[int(self.animation_idx)]

    def walk(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.walk_animation('left')
            self.rect.x -= 6
        elif keys[pygame.K_d]:
            self.walk_animation('right')
            self.rect.x += 6

    def apply_gravity(self):
        self.gravity += 0.7
        self.rect.y += self.gravity
        if self.rect.bottom >= 500:
            self.rect.bottom = 500

    def jump(self):
        if self.rect.bottom >= 500:
            self.gravity = -15
            self.image = self.player_jump

    def player_rect(self):
        return self.rect

    def boundary(self):
        if self.rect.left <= 200:
            self.rect.left = 200
        if self.rect.right >= 3500:
            self.rect.right = 3500

    def player_collision(self, player_sprite, obstacle, bool):
        if player_sprite is not None and pygame.sprite.spritecollide(player_sprite, obstacle, bool):
            if bool: self.health -= 3
            else:
                self.health -= 4
                self.gravity = -10
            impact_sound = pygame.mixer.Sound('audio/impact.ogg')
            pygame.mixer.Channel(1).play(impact_sound)

    def display_health(self):
        font_style = pygame.font.Font('font/Pixeltype.ttf', 50)
        health_surf = font_style.render(f'Health: {self.health}',False,(125, 209, 205))
        health_rect = health_surf.get_rect(topleft=(30, 30))
        pygame.display.get_surface().blit(health_surf, health_rect)

    def dead(self):
        if self.health <= 0:
            self.health = 100
            return True
        return False

    def player_reset(self):
        self.rect.midbottom = (300, 500)

    def update(self):
        self.walk()
        self.apply_gravity()
        self.boundary()

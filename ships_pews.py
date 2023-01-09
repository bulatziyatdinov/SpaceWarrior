import os
import sys
import pygame
from config import WIDTH, HEIGHT, SPEED_SETTINGS, ENEMY_HP, PLAYER_HP, ENEMY_FIRE_CHANCE
import random as rd

# Настройки
screen = pygame.display.set_mode((WIDTH, HEIGHT))
screen_rect = (0, 0, WIDTH, HEIGHT)
pygame.init()
pewenemy_sound = pygame.mixer.Sound("music/pewenemy.mp3")
pewenemy_sound.set_volume(0.1)

# Функция для ограничения значений
clamp = lambda value, minv, maxv: max(min(value, maxv), minv)


def cut_sheet(object, sheet, columns, rows):
    object.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
    for j in range(rows):
        for i in range(columns):
            frame_location = (object.rect.w * i, object.rect.h * j)
            object.frames.append(sheet.subsurface(pygame.Rect(frame_location, object.rect.size)))


# Функция загрузки изображений
def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


# Класс игрока
class PlayesShip(pygame.sprite.Sprite):
    image = load_image("player.png")
    image = pygame.transform.scale(image, (100, 75))

    def __init__(self, group):
        super().__init__(group)
        self.group = group
        self.image = PlayesShip.image
        self.damaged_image = pygame.transform.scale(load_image("player_dmg.png"), (100, 75))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = 10
        self.rect.y = 0
        self.hp = PLAYER_HP
        self.score = 0
        self.is_damaged = False

    def update(self, pos):
        self.rect.y = clamp(pos[1], 40, HEIGHT - 80)
        self.hp = max(self.hp, 0)
        if self.hp == 0:
            self.kill()


# Класс вражеского корабля 1
class EnemyShip(pygame.sprite.Sprite):
    image = load_image("enemyship.png")
    image = pygame.transform.scale(image, (80, 60))

    def __init__(self, group, y, x, speed, player):
        super().__init__(group)
        self.speed = speed
        self.player = player
        self.group = group
        self.image = EnemyShip.image
        self.damaged_image = pygame.transform.scale(load_image("enemyship2.png"), (80, 60))
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH - 50 + x
        self.rect.y = y
        self.hp = ENEMY_HP['BASE']
        self.is_damaged = False

    def update(self, pos):
        self.image = EnemyShip.image
        self.rect.x -= self.speed
        if self.hp == 0:
            self.player.score += 10
            self.kill()
        if self.rect.x <= 100:
            self.image = self.damaged_image
            self.player.hp -= 5
            self.player.score -= 10
            self.kill()
        if not self.rect.colliderect(screen_rect):
            self.player.score -= 10
            self.kill()


# Класс вражеского корабля 2
class EnemyShipOmega(pygame.sprite.Sprite):
    image = load_image("enemyshipomega.png")
    image = pygame.transform.scale(image, (80, 70))

    def __init__(self, group, y, x, speed, player, group2=None):
        super().__init__(group)
        self.group2 = group2
        self.speed = speed
        self.player = player
        self.group = group
        self.image = EnemyShipOmega.image
        self.damaged_image = pygame.transform.scale(load_image("enemyshipomega2.png"), (80, 70))
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH - 50 + x
        self.rect.y = y
        self.hp = ENEMY_HP['OMEGA']
        self.is_damaged = False
        self.cooldown_fire = 0

    def update(self, pos):
        self.image = EnemyShipOmega.image
        self.rect.x -= self.speed

        if not self.cooldown_fire:
            if not (rd.randint(0, ENEMY_FIRE_CHANCE)):
                self.cooldown_fire = 300
                pewenemy_sound.play(fade_ms=100)
                PewQuantum(self.group2, 4, 1, (self.rect.x, self.rect.y))
        else:
            self.cooldown_fire -= 1

        if self.hp == 0:
            self.player.score += 15
            self.kill()
        if self.rect.x <= 100:
            self.image = self.damaged_image
            self.player.hp -= 8
            self.player.score -= 20
            self.kill()
        if not self.rect.colliderect(screen_rect):
            self.player.score -= 20
            self.kill()


# Класс вражеского корабля 3
class EnemyShipSpeed(pygame.sprite.Sprite):
    image = load_image("enemyshipspeed.png")
    image = pygame.transform.scale(image, (60, 40))

    def __init__(self, group, y, x, speed, player):
        super().__init__(group)
        self.speed = speed + 2
        self.player = player
        self.group = group
        self.image = EnemyShipSpeed.image
        self.damaged_image = pygame.transform.scale(load_image("enemyshipspeed2.png"), (60, 40))
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH - 50 + x
        self.rect.y = y
        self.hp = ENEMY_HP['SPEED']
        self.is_damaged = False

    def update(self, pos):
        self.image = EnemyShipSpeed.image
        self.rect.x -= self.speed
        if self.hp == 0:
            self.player.score += 10
            self.kill()
        if self.rect.x <= 100:
            self.image = self.damaged_image
            self.player.hp -= 5
            self.player.score -= 10
            self.kill()
        if not self.rect.colliderect(screen_rect):
            self.player.score -= 10
            self.kill()


# Класс курсора
class Arrow(pygame.sprite.Sprite):
    image = load_image("arrow.png")

    def __init__(self, group):
        super().__init__(group)
        self.image = Arrow.image
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0

    def update(self, pos):
        self.rect.x = pos[0]
        self.rect.y = pos[1]


# Класс обычного выстрела
class PewBase(pygame.sprite.Sprite):
    image = load_image("pew1.png")

    def __init__(self, group, columns, rows, pos=(0, 0)):
        super().__init__(group)
        self.frames = []
        cut_sheet(self, PewBase.image, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(40, clamp(pos[1] + 20, 60, HEIGHT - 55))

    def update(self, pos):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        self.rect.x += SPEED_SETTINGS['BASE_SPEED']
        if not self.rect.colliderect(screen_rect):
            self.kill()


# Класс выстрела анти-материи
class PewAntimatter(pygame.sprite.Sprite):
    image = load_image("pew2.png")

    def __init__(self, group, columns, rows, pos=(0, 0)):
        super().__init__(group)
        self.frames = []
        cut_sheet(self, PewAntimatter.image, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(40, pos[1] + 20)

    def update(self, pos):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        self.rect.x += SPEED_SETTINGS['ANTIMATTER_SPEED']
        if not self.rect.colliderect(screen_rect):
            self.kill()


# Класс квантового выстрела
class PewQuantum(pygame.sprite.Sprite):
    image = load_image("pew3.png")
    image = pygame.transform.rotate(image, 180)

    def __init__(self, group, columns, rows, pos=(0, 0)):
        super().__init__(group)
        self.frames = []
        cut_sheet(self, PewQuantum.image, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(pos[0], pos[1] + 20)

    def update(self, pos, player):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        self.rect.x -= 5

        if not self.rect.colliderect(screen_rect):
            self.kill()

        if pygame.sprite.collide_mask(self, player):
            self.kill()
            player.image = player.damaged_image
            player.is_damaged = True
            player.hp -= 10
            player.hp = max(player.hp, 0)

import os
import random as rd
import sys

import pygame

from config import (ENEMY_FIRE_CHANCE, ENEMY_HP, HEIGHT, LEVEL_CHANCES, PLAYER_HP,
                    SPEED_SETTINGS, WIDTH)


# Настройки
screen = pygame.display.set_mode((WIDTH, HEIGHT))
screen_rect = (0, 0, WIDTH, HEIGHT)
pygame.init()
pewenemy_sound = pygame.mixer.Sound('sound/pewenemy.mp3')
pewenemy_sound.set_volume(0.1)


# Функция для ограничения значений
def clamp(value: int | float, min_value: int | float,
          max_value: int | float) -> int | float:
    if min_value > max_value:
        raise ValueError('Минимум > максимум')
    if value > max_value:
        return max_value
    elif value < min_value:
        return min_value
    else:
        return value


def cut_sheet(obj, sheet, columns, rows):
    obj.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                           sheet.get_height() // rows)
    for j in range(rows):
        for i in range(columns):
            frame_location = (obj.rect.w * i, obj.rect.h * j)
            obj.frames.append(
                sheet.subsurface(pygame.Rect(frame_location, obj.rect.size)))


# Функция загрузки изображений
def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f'Файл с изображением "{fullname}" не найден')
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


class ShipBase(pygame.sprite.Sprite):
    default_image = None

    def __init__(self, group):
        super().__init__(group)
        self.image = self.default_image
        self.group = group

    def update(self, pos):
        pass


# Класс игрока
class PlayerShip(ShipBase):
    default_image = pygame.transform.scale(
        load_image('player.png'), (100, 75))
    default_damaged_image = pygame.transform.scale(
        load_image('player_dmg.png'), (100, 75))

    def __init__(self, group):
        super().__init__(group)
        self.rect = self.image.get_rect()
        self.rect.x = 10
        self.rect.y = 0
        self.hp = PLAYER_HP
        self.score = 0
        self.is_damaged = False

    def update(self, pos) -> None:
        self.rect.y = clamp(pos[1], 40, HEIGHT - 80)
        if self.hp == 0:
            self.kill()

    def is_alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, damage: int) -> None:
        self.hp = max(self.hp - damage, 0)


# Класс вражеского корабля 1
class EnemyShip(ShipBase):
    default_image = pygame.transform.scale(
        load_image('enemyship.png'), (80, 60))
    default_damaged_image = pygame.transform.scale(
        load_image('enemyship2.png'), (80, 60))

    def __init__(self, group, y, x, speed, player: PlayerShip):
        super().__init__(group)
        self.speed = speed
        self.player = player
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH - 50 + x
        self.rect.y = y
        self.hp = ENEMY_HP['BASE']
        self.is_damaged = False

    def update(self, pos):
        self.image = self.default_image
        self.rect.x -= self.speed
        if self.hp == 0:
            self.player.score += 10
            self.kill()
        if self.rect.x <= 100:
            self.image = self.default_damaged_image
            self.player.take_damage(5)
            self.player.score -= 10
            self.kill()
        if not self.rect.colliderect(screen_rect):
            self.player.score -= 10
            self.kill()


# Класс вражеского корабля 2
class EnemyShipOmega(ShipBase):
    default_image = pygame.transform.scale(
        load_image('enemyshipomega.png'), (80, 70))
    default_damaged_image = pygame.transform.scale(
            load_image('enemyshipomega2.png'), (80, 70))

    def __init__(self, group, y, x, speed, player: PlayerShip, group2=None):
        super().__init__(group)
        self.group2 = group2
        self.speed = speed
        self.player = player
        self.image = self.default_image
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH - 50 + x
        self.rect.y = y
        self.hp = ENEMY_HP['OMEGA']
        self.is_damaged = False
        self.cooldown_fire = 0

    def update(self, pos):
        self.image = self.default_image
        self.rect.x -= self.speed

        if not self.cooldown_fire:
            if not (rd.randint(0, ENEMY_FIRE_CHANCE)):
                self.cooldown_fire = 300
                pewenemy_sound.play(fade_ms=100)
                PewQuantum(self.group2, 4, 1,
                           (self.rect.x, self.rect.y), self.player)
        else:
            self.cooldown_fire -= 1

        if self.hp == 0:
            self.player.score += 15
            self.kill()
        if self.rect.x <= 100:
            self.image = self.default_damaged_image
            self.player.take_damage(8)
            self.player.score -= 20
            self.kill()
        if not self.rect.colliderect(screen_rect):
            self.player.score -= 20
            self.kill()


# Класс вражеского корабля 3
class EnemyShipSpeed(ShipBase):
    default_image = pygame.transform.scale(
        load_image('enemyshipspeed.png'), (60, 40))
    default_damaged_image = pygame.transform.scale(
        load_image('enemyshipspeed2.png'), (60, 40))

    def __init__(self, group, y, x, speed, player: PlayerShip):
        super().__init__(group)
        self.speed = speed
        self.player = player
        self.image = self.default_image
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH - 50 + x
        self.rect.y = y
        self.hp = ENEMY_HP['SPEED']
        self.is_damaged = False

    def update(self, pos):
        self.image = self.default_image
        self.rect.x -= self.speed
        if self.hp == 0:
            self.player.score += 10
            self.kill()
        if self.rect.x <= 100:
            self.image = self.default_damaged_image
            self.player.take_damage(5)
            self.player.score -= 10
            self.kill()
        if not self.rect.colliderect(screen_rect):
            self.player.score -= 10
            self.kill()


# Класс обычного выстрела
class PewBase(pygame.sprite.Sprite):
    default_image = load_image('pew1.png')

    def __init__(self, group, columns, rows, pos=(0, 0)):
        super().__init__(group)
        self.frames = []
        cut_sheet(self, self.default_image, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(
            40, clamp(pos[1] + 20, 60, HEIGHT - 55))

    def update(self, pos):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        self.rect.x += SPEED_SETTINGS['BASE_SPEED']
        if not self.rect.colliderect(screen_rect):
            self.kill()


# Класс выстрела анти-материи
class PewAntimatter(pygame.sprite.Sprite):
    default_image = load_image('pew2.png')

    def __init__(self, group, columns, rows, pos=(0, 0)):
        super().__init__(group)
        self.frames = []
        cut_sheet(self, self.default_image, columns, rows)
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
    default_image = pygame.transform.rotate(
        load_image('pew3.png'), 180)

    def __init__(self, group, columns, rows, pos, player: PlayerShip):
        super().__init__(group)
        self.frames = []
        self.player = player
        cut_sheet(self, self.default_image, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(pos[0], pos[1] + 20)

    def update(self, pos):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        self.rect.x -= 5

        if not self.rect.colliderect(screen_rect):
            self.kill()

        if pygame.sprite.collide_mask(self, self.player):
            self.kill()
            self.player.image = self.player.default_damaged_image
            self.player.is_damaged = True
            self.player.take_damage(10)


# Класс курсора
class Arrow(pygame.sprite.Sprite):
    default_image = load_image('arrow.png')

    def __init__(self, group):
        super().__init__(group)
        self.image = self.default_image
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0

    def update(self, pos):
        self.rect.x, self.rect.y = pos


def random_spawn(group, player, level=1, group2=None):
    res = []
    n = rd.randint(3, 7)

    yyy_1 = rd.sample(list(range(50, HEIGHT - 60, 70)), k=n)

    yyy_2_list = list(range(50, HEIGHT - 60, 70))

    for y in yyy_1:
        ship_type = rd.randint(LEVEL_CHANCES[level][0], LEVEL_CHANCES[level][1])
        x = rd.randrange(-25, 25)
        sp = SPEED_SETTINGS['ENEMY_SPEED']
        speed = rd.randrange(sp[0], sp[1])
        if ship_type:
            res.append(EnemyShip(group, y, x, speed, player))
        else:
            res.append(EnemyShipOmega(group, y, x, speed, player, group2))
            if level == 3:
                if rd.randint(0, 1):
                    yyy_2 = rd.choice(yyy_2_list)
                    res.append(EnemyShipSpeed(group, yyy_2, x, speed, player))
    return res

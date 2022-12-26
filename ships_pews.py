import os
import sys
import pygame
from config import WIDTH, HEIGHT, SPEED_SETTINGS, ENEMY_HP, PLAYER_HP
import random as rd

# Настройки
screen = pygame.display.set_mode((WIDTH, HEIGHT))
screen_rect = (0, 0, WIDTH, HEIGHT)

# Функция для ограничения значений
clamp = lambda value, minv, maxv: max(min(value, maxv), minv)


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    # прозрачный цвет
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


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
        self.hp = clamp(self.hp, 0, 100)
        if self.hp == 0:
            self.kill()


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
            if not (rd.randint(0, 100)):
                self.cooldown_fire = 300
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
        self.cut_sheet(PewBase.image, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(40, clamp(pos[1] + 20, 60, HEIGHT - 55))

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

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
        self.cut_sheet(PewAntimatter.image, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(40, pos[1] + 20)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

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
        self.cut_sheet(PewQuantum.image, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(pos[0], pos[1] + 20)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

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

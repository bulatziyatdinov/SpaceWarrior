import random as rd
import pygame
from config import HEIGHT, SPEED_SETTINGS, WIN_SCORE
from ships_pews import EnemyShip, EnemyShipOmega


class Button:
    def __init__(self, x, y, width, height, screen, font, container, buttonText='Button', onclickFunction=None,
                 onePress=False):
        self.x = x
        self.y = y
        self.skip = False
        self.screen = screen
        self.font = font
        self.container = container
        self.width = width
        self.height = height
        self.onclickFunction = onclickFunction
        self.onePress = onePress
        self.alreadyPressed = False

        self.fillColors = {
            'normal': '#ffffff',
            'hover': '#666666',
            'pressed': '#333333',
        }

        self.buttonSurface = pygame.Surface((self.width, self.height))
        self.buttonRect = pygame.Rect(self.x, self.y, self.width, self.height)

        self.buttonSurf = self.font.render(buttonText, True, (20, 20, 20))

        container.append(self)

    def process(self, pos):
        self.buttonSurface.fill(self.fillColors['normal'])
        if self.buttonRect.collidepoint(pos):
            self.buttonSurface.fill(self.fillColors['hover'])
            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                self.buttonSurface.fill(self.fillColors['pressed'])
                if self.onePress:
                    self.onclickFunction(self)
                elif not self.alreadyPressed:
                    self.onclickFunction(self)
                    self.alreadyPressed = True
            else:
                self.alreadyPressed = False

        self.buttonSurface.blit(self.buttonSurf, [
            self.buttonRect.width / 2 - self.buttonSurf.get_rect().width / 2,
            self.buttonRect.height / 2 - self.buttonSurf.get_rect().height / 2
        ])
        self.screen.blit(self.buttonSurface, self.buttonRect)


# Рандомный спавн врагов
def random_spawn(group, player, level=1, group2=None):
    res = []
    n = rd.randint(3, 7)

    yyy = list(range(50, HEIGHT - 60, 70))
    yyy = rd.sample(yyy, k=n)

    ship_type = 1
    for y in yyy:
        if level == 2:
            ship_type = rd.randint(0, 6)
        x = rd.randrange(-25, 25)
        sp = SPEED_SETTINGS['ENEMY_SPEED']
        speed = rd.randrange(sp[0], sp[1])
        if ship_type:
            res.append(EnemyShip(group, y, x, speed, player))
        else:
            res.append(EnemyShipOmega(group, y, x, speed, player, group2))
    return res


class DataText:
    def __init__(self, file_start, file_end1, file_end2):
        try:
            with open(f"text/{file_start}", 'r', encoding='utf-8') as f:
                temp = f.readlines()
            self.data_start = list(map(str.strip, temp))
            self.data_start[-1] += f' {WIN_SCORE}'
        except Exception as ex:
            self.data_start = []
            print('Error:', ex)

        try:
            with open(f"text/{file_end1}", 'r', encoding='utf-8') as f:
                temp = f.readlines()
            self.data_end1 = list(map(str.strip, temp))
        except Exception as ex:
            self.data_end1 = []
            print('Error:', ex)

        try:
            with open(f"text/{file_end2}", 'r', encoding='utf-8') as f:
                temp = f.readlines()
            self.data_end2 = list(map(str.strip, temp))
        except Exception as ex:
            self.data_end2 = []
            print('Error:', ex)

    def info(self):
        print(self.data_start)
        print(self.data_end1)
        print(self.data_end2)

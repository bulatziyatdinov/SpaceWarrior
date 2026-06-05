import random as rd

import pygame
from pygame.sprite import Group

from config import HEIGHT, WIDTH, WIN_SCORE_BASE
from ships_pews import load_image


def write_record_result(score: int) -> None:
    """Writes results of endless level into records.txt"""
    try:
        with open('records.txt', 'a', encoding='utf-8') as f:
            f.write(f'{score}\n')
    except Exception as ex:
        print('Error: ', ex)


def get_record_result() -> int:
    """Gets results of endless level from records.txt"""
    try:
        with open('records.txt', 'r', encoding='utf-8') as f:
            temp = f.readlines()
        temp = max(tuple(map(lambda x: int(x.rstrip()), temp)))
        return temp
    except FileNotFoundError:
        return 0


# Класс кнопок
class Button:
    """
    Class for Buttons. I do not remember where I got it from.
    Perhaps it is Yandex Lyceum code what they gave us
    """
    def __init__(self, x: int, y: int, width: int, height: int, screen, font, container,
                 buttonText='Button', onclickFunction=None, onePress=False):
        self.skip = False
        self.screen = screen
        self.font = font
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
        self.buttonRect = pygame.Rect(x, y, self.width, self.height)
        self.buttonSurf = self.font.render(buttonText, True, (20, 20, 20))
        container.append(self)

    def process(self, pos: tuple[int, int]) -> None:
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


class DataText:
    """
    Class that stores text for the main menu and endings
    """
    def __init__(self, file_start: str, file_end1: str, file_end2: str):
        try:
            with open(f'text/{file_start}', 'r', encoding='utf-8') as f:
                self.data_start = list(map(str.strip, f.readlines()))
            self.data_start[-1] += f' {WIN_SCORE_BASE} очков'
        except Exception as ex:
            self.data_start = []
            print('Error:', ex)

        try:
            with open(f'text/{file_end1}', 'r', encoding='utf-8') as f:
                self.data_end1 = list(map(str.strip, f.readlines()))
        except Exception as ex:
            self.data_end1 = []
            print('Error:', ex)

        try:
            with open(f'text/{file_end2}', 'r', encoding='utf-8') as f:
                self.data_end2 = list(map(str.strip, f.readlines()))
        except Exception as ex:
            self.data_end2 = []
            print('Error:', ex)


class Particle(pygame.sprite.Sprite):
    """
    Class from Yandex Lyceum for particles on the final screen
    """
    fire = [load_image('star.png')]

    for scale in (4, 8, 12):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, group: Group, gravity:  int | float, pos: tuple[int, int],
                 dx: int, dy: int):
        super().__init__(group)
        self.image = rd.choice(self.fire)
        self.group = group
        self.container = (0, 0, WIDTH, HEIGHT)
        self.gravity = gravity
        self.rect = self.image.get_rect()

        self.velocity = [dx, dy]

        self.rect.x, self.rect.y = pos

    def update(self) -> None:
        self.velocity[1] += self.gravity

        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]

        if not self.rect.colliderect(self.container):
            self.kill()


def create_particles(group: Group,
                     gravity: int | float,
                     particle_count: int = 20) -> None:
    """Create particles with physics"""
    numbers = range(-5, 6)
    position = (rd.randint(0, WIDTH), rd.randint(0, HEIGHT))
    for _ in range(particle_count):
        Particle(group, gravity, position,
                 rd.choice(numbers), rd.choice(numbers))

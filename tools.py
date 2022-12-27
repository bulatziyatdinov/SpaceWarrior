import pygame
from config import WIDTH, HEIGHT, SPEED_SETTINGS, WIN_SCORE_BASE, LEVEL_CHANCHES
from ships_pews import EnemyShip, EnemyShipOmega, load_image
import random as rd


# Рандомный спавн врагов
def random_spawn(group, player, level=1, group2=None):
    res = []
    n = rd.randint(3, 7)

    yyy = list(range(50, HEIGHT - 60, 70))
    yyy = rd.sample(yyy, k=n)

    for y in yyy:
        ship_type = rd.randint(LEVEL_CHANCHES[level][0], LEVEL_CHANCHES[level][1])
        x = rd.randrange(-25, 25)
        sp = SPEED_SETTINGS['ENEMY_SPEED']
        speed = rd.randrange(sp[0], sp[1])
        if ship_type:
            res.append(EnemyShip(group, y, x, speed, player))
        else:
            res.append(EnemyShipOmega(group, y, x, speed, player, group2))
    return res


def write_results(score: int):
    try:
        with open('records.txt', 'a', encoding='utf-8') as f:
            f.write(f'{score}\n')
    except Exception as ex:
        print('Error: ', ex)


def record_result() -> int | str:
    try:
        with open('records.txt', 'r', encoding='utf-8') as f:
            temp = f.readlines()
        temp = max(tuple(map(str.rstrip, temp)))
        return temp
    except Exception:
        return '###'


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


class DataText:
    def __init__(self, file_start, file_end1, file_end2):
        try:
            with open(f"text/{file_start}", 'r', encoding='utf-8') as f:
                temp = f.readlines()
            self.data_start = list(map(str.strip, temp))
            self.data_start[-1] += f' {WIN_SCORE_BASE}'
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


# Генератор частиц
class Particle(pygame.sprite.Sprite):
    fire = [load_image("star.png")]

    for scale in (4, 8, 12):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, group, gravity, pos, dx, dy):
        super().__init__(group)
        self.image = rd.choice(self.fire)
        self.group = group
        self.container = (0, 0, WIDTH, HEIGHT)
        self.gravity = gravity
        self.rect = self.image.get_rect()

        self.velocity = [dx, dy]

        self.rect.x, self.rect.y = pos

    def update(self):
        self.velocity[1] += self.gravity

        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]

        if not self.rect.colliderect(self.container):
            self.kill()


def create_particles(group, gravity, particle_count=20):
    numbers = range(-5, 6)
    position = (rd.randint(0, WIDTH), rd.randint(0, HEIGHT))
    for _ in range(particle_count):
        Particle(group, gravity, position, rd.choice(numbers), rd.choice(numbers))

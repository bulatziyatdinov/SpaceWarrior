import sys
import pygame as pg
from config import *
from ships_pews import PlayesShip, Arrow, PewBase, PewAntimatter, load_image, EnemyShip, EnemyShipSpeed, EnemyShipOmega
from tools import random_spawn, Button, DataText, create_particles, write_results, record_result

# ФПС
clock = pg.time.Clock()

# Нужные вещи
pg.init()
pg.mixer.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.mouse.set_visible(False)

# Необходимые флаги
running = True
show_mouse = False
is_start = True
is_end = False

# Бэкграунды
background_image = load_image('background2.png')
background_image = pg.transform.scale(background_image, (WIDTH, HEIGHT))

background_start_image = load_image('background3.png')
background_start_image = pg.transform.scale(background_start_image, (WIDTH, HEIGHT))

background_end_image = load_image('background4.png')
background_end_image = pg.transform.scale(background_end_image, (WIDTH, HEIGHT))

# Шрифты
FONT = pg.font.SysFont('Arial', 20)
MENU_FONT = pg.font.SysFont('Arial', 20)
END_FONT = pg.font.SysFont('Arial', 36)

# Текст
TEXT = DataText('start_text.txt', 'end_text_good.txt', 'end_text_bad.txt')

# Кулдаун оружия
cooldown_base = 0
cooldown_antimatter = 0
cooldown_dmg = 10
cooldown_enemy = 0

# Debug
debug_mode = DEBUG_SETTINGS

# Номер уровня
level = 1

# Очки для конца
win_score = WIN_SCORE_BASE

# Название окна
pg.display.set_caption(NAME)

# Иконка окна
pygame_icon = load_image('player2.png')
pg.display.set_icon(pygame_icon)

# Группы спрайтов
all_sprites = pg.sprite.Group()
player_sprite_group = pg.sprite.Group()
arrow_sprite_group = pg.sprite.Group()
particles_sprite_group = pg.sprite.Group()

bluster_sprite_group = pg.sprite.Group()
antimatter_sprite_group = pg.sprite.Group()
enemy_bluster_sprite_group = pg.sprite.Group()
enemy_ship_sprite_group = pg.sprite.Group()
btns = []
btn_end = []

TEST_sprite_group = pg.sprite.Group()

player = PlayesShip(player_sprite_group)
arrow = Arrow(arrow_sprite_group)

record = record_result()
print(record)


# Функции кнопок
def btn1_onclick(object):
    global level
    level = 1
    object.skip = True


def btn2_onclick(object):
    global level
    level = 2
    object.skip = True


def btn3_onclick(object):
    global running, record
    if level == 3:
        write_results(player.score)
    record = record_result()
    running = False


def btn5_onclick(object):
    global is_start, is_end, cooldown_base, cooldown_antimatter, cooldown_dmg, cooldown_enemy, player, record
    for i in bluster_sprite_group:
        i.kill()
    for i in antimatter_sprite_group:
        i.kill()
    for i in enemy_bluster_sprite_group:
        i.kill()
    for i in enemy_ship_sprite_group:
        i.kill()

    cooldown_base = 0
    cooldown_antimatter = 0
    cooldown_dmg = 0
    cooldown_enemy = 50

    btn1.skip = False
    btn2.skip = False
    btn6.skip = False

    is_start = True
    is_end = False

    if level == 3:
        write_results(player.score)
    record = record_result()

    player = PlayesShip(player_sprite_group)


def btn6_onclick(object):
    global win_score, level
    win_score = 999999
    level = 3
    object.skip = True


# Кнопки
btn1 = Button(WIDTH - 200, HEIGHT - 265, 150, 50, screen, MENU_FONT, btns, 'Уровень 1', btn1_onclick)
btn2 = Button(WIDTH - 200, HEIGHT - 195, 150, 50, screen, MENU_FONT, btns, 'Уровень 2', btn2_onclick)
btn6 = Button(WIDTH - 200, HEIGHT - 125, 150, 50, screen, MENU_FONT, btns, 'Бесконечный', btn6_onclick)
btn3 = Button(WIDTH - 200, HEIGHT - 55, 150, 50, screen, MENU_FONT, btns, 'Выход', btn3_onclick)

btn5 = Button(WIDTH // 2 - 250, HEIGHT - 150, 150, 50, screen, MENU_FONT, btn_end, 'Главная', btn5_onclick)
btn4 = Button(WIDTH // 2 + 100, HEIGHT - 150, 150, 50, screen, MENU_FONT, btn_end, 'Выход', btn3_onclick)

# Основной цикл
while running:
    is_freeze = not (is_start or is_end)
    pressed_keys = pg.key.get_pressed()
    pos = pg.mouse.get_pos()
    show_mouse = False

    if (player.score >= win_score) or player.hp == 0:
        is_end = True

    if debug_mode:
        pg.display.set_caption(
            NAME + ' | ' + str(clock.get_fps())[:4] + f' FPS | LVL: {level} | WIN: {win_score} | [DEBUG]')

    # Цикл событий
    for event in pg.event.get():
        # Выход, старт и дебаг режим
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                running = False
            if event.key == pg.K_TAB:
                if debug_mode:
                    debug_mode = False
                    pg.display.set_caption(NAME)
                else:
                    debug_mode = True


        # Кнопки мыши
        elif event.type == pg.MOUSEBUTTONDOWN:
            if is_freeze:
                if event.button == 1:
                    if (not cooldown_base) and (player.hp != 0):
                        PewBase(bluster_sprite_group, 4, 1, pos)
                        cooldown_base = COOLDOWN_LIST['BASE']
                if event.button == 2:
                    if (not cooldown_base) and (player.hp != 0) and (debug_mode):
                        player.score += 1000
                elif event.button == 3:
                    if (not cooldown_antimatter) and (not is_end):
                        PewAntimatter(antimatter_sprite_group, 4, 1, pos)
                        cooldown_antimatter = COOLDOWN_LIST['ANTIMATTER']


    # Обновление поля
    def draw_screen():
        if is_start:
            screen.blit(background_start_image, (0, 0))
        elif is_end:
            screen.blit(background_end_image, (0, 0))
        else:
            screen.blit(background_image, (0, 0))


    # Если не начало или конец
    def main_part():
        global cooldown_enemy, cooldown_dmg
        pg.event.set_grab(True)

        if pg.mouse.get_focused():
            # Если мышь в области экрана, двигаем корабль
            pos = pg.mouse.get_pos()
            player_sprite_group.update(pos)

            if cooldown_enemy == 0:
                res = random_spawn(enemy_ship_sprite_group, player, level, enemy_bluster_sprite_group)
                for i in res:
                    i
                cooldown_enemy = COOLDOWN_LIST['ENEMY']

            hits = pg.sprite.groupcollide(enemy_ship_sprite_group, bluster_sprite_group, False, True)
            for hit in hits:
                if isinstance(hit, EnemyShip):
                    hit.image = hit.damaged_image
                    hit.hp = max(0, hit.hp - DAMAGE_LIST['BASE'])
                elif isinstance(hit, EnemyShipSpeed):
                    hit.image = hit.damaged_image
                    hit.hp = max(0, hit.hp - DAMAGE_LIST['BASE'])
                elif isinstance(hit, EnemyShipOmega):
                    hit.image = hit.damaged_image
                    hit.hp = max(0, hit.hp - DAMAGE_LIST['BASE'])

            hits = pg.sprite.groupcollide(enemy_ship_sprite_group, antimatter_sprite_group, False, False)
            for hit in hits:
                hit.image = hit.damaged_image
                hit.hp = max(0, hit.hp - DAMAGE_LIST['ANTIMATTER'])

            hits = pg.sprite.groupcollide(player_sprite_group, enemy_ship_sprite_group, False, True)
            for hit in hits:
                hit.hp -= DAMAGE_LIST['ENEMY']
                player.is_damaged = True

            pg.sprite.groupcollide(bluster_sprite_group, enemy_bluster_sprite_group, True, True)

            pg.sprite.groupcollide(antimatter_sprite_group, enemy_bluster_sprite_group, False, True)

            # Покраснение при попадании
            if player.is_damaged:
                cooldown_dmg = COOLDOWN_LIST['DMG']
                player.is_damaged = False
            if not (cooldown_dmg):
                player.image = PlayesShip.image


    # ОТРИСОВКА СПРАЙТОВ
    def draw_all_sprites():
        global cooldown_enemy
        bluster_sprite_group.draw(screen)

        antimatter_sprite_group.draw(screen)

        enemy_bluster_sprite_group.draw(screen)

        player_sprite_group.draw(screen)

        enemy_ship_sprite_group.draw(screen)

        if pg.mouse.get_focused():
            bluster_sprite_group.update(pos)
            antimatter_sprite_group.update(pos)
            enemy_bluster_sprite_group.update(pos, player)
            enemy_ship_sprite_group.update(pos)


    # Отрисовка показателей
    def draw_nums():
        FONT = pg.font.SysFont('Arial', 20)

        if cooldown_base:
            cooldown_blaster_info = FONT.render(f'Бластер: {cooldown_base}', True, (255, 0, 0))
        else:
            cooldown_blaster_info = FONT.render(f'Бластер: ГОТОВ', True, (0, 255, 0))

        if cooldown_antimatter:
            cooldown_antimatter_info = FONT.render(f'Анти-материя: {cooldown_antimatter}', True, (255, 0, 0))
        else:
            cooldown_antimatter_info = FONT.render(f'Анти-материя: ГОТОВ', True, (0, 255, 0))

        hp_status = FONT.render(f'ХП: {player.hp}', True, (200, 0, 255))
        score_status = FONT.render(f'Очки: {player.score}', True, (200, 0, 255))
        enemy_status = FONT.render(f'След. волна: {cooldown_enemy}', True, (200, 0, 255))
        lvl_status = FONT.render(f'Уровень: {level}', True, (200, 0, 255))

        screen.blit(hp_status, (10, 10))
        screen.blit(score_status, (100, 10))
        screen.blit(cooldown_blaster_info, (200, 10))
        screen.blit(cooldown_antimatter_info, (360, 10))
        screen.blit(enemy_status, (580, 10))
        screen.blit(lvl_status, (800, 10))


    # Обновление кулдауна
    def cooldown_update():
        global cooldown_base, cooldown_antimatter, cooldown_dmg, cooldown_enemy
        if pg.mouse.get_focused():
            if cooldown_base:
                cooldown_base -= 1
            if cooldown_antimatter:
                cooldown_antimatter -= 1
            if cooldown_dmg:
                cooldown_dmg -= 1
            if cooldown_enemy:
                cooldown_enemy -= 1


    # Отрисовка экрана
    draw_screen()

    if is_freeze:
        main_part()
        cooldown_update()
        draw_all_sprites()
        draw_nums()


    # Функция для экрана на старте
    def start():
        global show_mouse
        show_mouse = True
        for i in range(len(TEXT.data_start)):
            start = END_FONT.render(TEXT.data_start[i], True, (255, 255, 255))
            screen.blit(start, (WIDTH // 2 - 400, HEIGHT // 2 + 40 * i - 200))
        rec = END_FONT.render(f'Рекорд бесконечного режима: {record}', True, (200, 0, 255))
        screen.blit(rec, (100, HEIGHT - 100))


    # Функция для экрана в конце
    def end():
        global show_mouse
        pg.event.set_grab(False)
        show_mouse = True

        end_score = f'Всего очков: {player.score}'

        if player.hp == 0:
            end_message1 = TEXT.data_end2[0]
            end_message2 = TEXT.data_end2[1]
        else:
            end_message1 = TEXT.data_end1[0]
            end_message2 = TEXT.data_end1[1]
            create_particles(particles_sprite_group, GRAVITY, 1)
            particles_sprite_group.draw(screen)
            particles_sprite_group.update()

        end1 = END_FONT.render(end_message1, True, (255, 255, 255))
        end2 = END_FONT.render(end_message2, True, (255, 255, 255))
        end_scr = END_FONT.render(end_score, True, (255, 255, 255))

        screen.blit(end1, (WIDTH // 2 - 300, HEIGHT // 2 - 40))
        screen.blit(end2, (WIDTH // 2 - 300, HEIGHT // 2))
        screen.blit(end_scr, (WIDTH // 2 - 300, HEIGHT // 2 + 80))

        for i in btn_end:
            i.process(pos)


    # Начальный экран
    if is_start:
        if btn1.skip or btn2.skip or btn6.skip:
            is_start = False
        start()
        for i in btns:
            i.process(pos)

    # Конечный экран
    if is_end:
        win_score = WIN_SCORE_BASE
        end()

    # Отрисовка мыши
    if pg.mouse.get_focused() and show_mouse:
        arrow_sprite_group.update(pos)
        arrow_sprite_group.draw(screen)


    # Обновдение параметров
    def update_all():
        clock.tick(FPS)
        pg.display.update()
        pg.display.flip()


    update_all()

    player.hp = max(0, player.hp)

pg.quit()
sys.exit()

import sys

import pygame as pg

import config
from ships_pews import (Arrow, EnemyShip, EnemyShipOmega, EnemyShipSpeed, 
                        load_image, PewAntimatter, PewBase, PlayesShip)
from tools import (random_spawn, Button, DataText, create_particles,
                   write_results, record_result)


# ФПС
clock = pg.time.Clock()

# Нужные вещи
pg.init()

screen = pg.display.set_mode((config.WIDTH, config.HEIGHT))
pg.mouse.set_visible(False)

# Необходимые флаги
running = False

if __name__ == '__main__':
    running = True

show_mouse = False
is_start = True
is_end = False
play_music = True

# Задние фоны
background_image = pg.transform.scale(
    load_image('background2.png'), (config.WIDTH, config.HEIGHT))
background_start_image = pg.transform.scale(
    load_image('background3.png'), (config.WIDTH, config.HEIGHT))
background_end_image = pg.transform.scale(
    load_image('background4.png'), (config.WIDTH, config.HEIGHT))

# Шрифты
FONT = pg.font.SysFont('Arial', 20)
MENU_FONT = pg.font.SysFont('Arial', 20)
END_FONT = pg.font.SysFont('Arial', 36)

# Текст
TEXT = DataText(
    'start_text.txt',
    'end_text_good.txt',
    'end_text_bad.txt',
)

# Перезарядка оружия (в кадрах)
cooldown_base = 0
cooldown_antimatter = 0
cooldown_dmg = 10
cooldown_enemy = 0

# Debug-режим
debug_mode = config.DEBUG_SETTINGS

# Номер текущего уровня
level = 1

# Очки для конца
win_score = config.WIN_SCORE_BASE

# Название окна
pg.display.set_caption(config.NAME)

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

# Списки кнопок
btns = []
btn_end = []

TEST_sprite_group = pg.sprite.Group()

player = PlayesShip(player_sprite_group)
arrow = Arrow(arrow_sprite_group)

record = record_result()

# Музыка
theme_sound = pg.mixer.Sound("music/main_music.mp3")
pew_sound = pg.mixer.Sound("music/pew.wav")
pewantimatter_sound = pg.mixer.Sound("music/antimatter.mp3")

theme_sound.set_volume(0.1)
pew_sound.set_volume(0.1)
pewantimatter_sound.set_volume(0.1)

theme_sound.play(-1)


# Функции кнопок
def btn1_onclick(obj):
    global level
    level = 1
    theme_sound.set_volume(0.05)
    obj.skip = True


def btn2_onclick(obj):
    global level
    level = 2
    theme_sound.set_volume(0.05)
    obj.skip = True


def btn3_onclick(obj):
    global running, record
    if level == 3:
        write_results(player.score)
    record = record_result()
    running = False


def btn5_onclick():
    global is_start, is_end, cooldown_base, cooldown_antimatter, \
        cooldown_dmg, cooldown_enemy, player, record
    for obj in bluster_sprite_group:
        obj.kill()
    for obj in antimatter_sprite_group:
        obj.kill()
    for obj in enemy_bluster_sprite_group:
        obj.kill()
    for obj in enemy_ship_sprite_group:
        obj.kill()

    cooldown_base = 0
    cooldown_antimatter = 0
    cooldown_dmg = 0
    cooldown_enemy = 50

    btn1.skip = False
    btn2.skip = False
    btn6.skip = False

    is_start = True
    is_end = False

    theme_sound.set_volume(0.1)

    if level == 3:
        write_results(player.score)
    record = record_result()

    player = PlayesShip(player_sprite_group)


def btn6_onclick(obj):
    global win_score, level
    win_score = 999999
    level = 3
    theme_sound.set_volume(0.05)
    obj.skip = True


def btn7_onclick(obj):
    global play_music
    if play_music:
        play_music = False
        theme_sound.set_volume(0)
    else:
        play_music = True
        theme_sound.set_volume(0.1)


# Кнопки
btn1 = Button(config.WIDTH - 200, config.HEIGHT - 265, 150, 50, screen, MENU_FONT, btns, 'Уровень 1', btn1_onclick)
btn2 = Button(config.WIDTH - 200, config.HEIGHT - 195, 150, 50, screen, MENU_FONT, btns, 'Уровень 2', btn2_onclick)
btn6 = Button(config.WIDTH - 200, config.HEIGHT - 125, 150, 50, screen, MENU_FONT, btns, 'Бесконечный', btn6_onclick)
btn3 = Button(config.WIDTH - 200, config.HEIGHT - 55, 150, 50, screen, MENU_FONT, btns, 'Выход', btn3_onclick)
btn7 = Button(10, config.HEIGHT - 60, 70, 50, screen, MENU_FONT, btns, 'Музыка', btn7_onclick)

btn5 = Button(config.WIDTH // 2 - 250, config.HEIGHT - 150, 150, 50, screen, MENU_FONT, btn_end, 'Главная', btn5_onclick)
btn4 = Button(config.WIDTH // 2 + 100, config.HEIGHT - 150, 150, 50, screen, MENU_FONT, btn_end, 'Выход', btn3_onclick)

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
            config.NAME + ' | ' + str(clock.get_fps())[:4] + f' FPS | LVL: {level} | WIN: {win_score} | [DEBUG]')

    # Цикл событий
    for event in pg.event.get():
        # Выход, старт и дебаг режим
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                running = False
            elif event.key == pg.K_SPACE:
                if debug_mode:
                    if not is_end:
                        is_end = True
                        is_start = False
                    else:
                        is_end = False
                        is_start = True
                        btn5_onclick()
            elif event.key == pg.K_TAB:
                if debug_mode:
                    debug_mode = False
                    pg.display.set_caption(config.NAME)
                else:
                    debug_mode = True


        # Кнопки мыши
        elif event.type == pg.MOUSEBUTTONDOWN:
            if is_freeze:
                if event.button == 1:
                    if (not cooldown_base) and (player.hp != 0):
                        pew_sound.play()
                        PewBase(bluster_sprite_group, 4, 1, pos)
                        cooldown_base = config.COOLDOWN_LIST['BASE']
                if event.button == 2:
                    if (not cooldown_base) and (player.hp != 0) and (debug_mode):
                        player.score += 100
                elif event.button == 3:
                    if (not cooldown_antimatter) and (not is_end):
                        pewantimatter_sound.play()
                        PewAntimatter(antimatter_sprite_group, 4, 1, pos)
                        cooldown_antimatter = config.COOLDOWN_LIST['ANTIMATTER']


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
                cooldown_enemy = config.COOLDOWN_LIST['ENEMY']

            hits = pg.sprite.groupcollide(enemy_ship_sprite_group, bluster_sprite_group, False, True)
            for hit in hits:
                if isinstance(hit, EnemyShip):
                    hit.image = hit.damaged_image
                    hit.hp = max(0, hit.hp - config.DAMAGE_LIST['BASE'])
                elif isinstance(hit, EnemyShipSpeed):
                    hit.image = hit.damaged_image
                    hit.hp = max(0, hit.hp - config.DAMAGE_LIST['BASE'])
                elif isinstance(hit, EnemyShipOmega):
                    hit.image = hit.damaged_image
                    hit.hp = max(0, hit.hp - config.DAMAGE_LIST['BASE'])

            hits = pg.sprite.groupcollide(enemy_ship_sprite_group, antimatter_sprite_group, False, False)
            for hit in hits:
                hit.image = hit.damaged_image
                hit.hp = max(0, hit.hp - config.DAMAGE_LIST['ANTIMATTER'])

            hits = pg.sprite.groupcollide(player_sprite_group, enemy_ship_sprite_group, False, True)
            for hit in hits:
                hit.hp -= config.DAMAGE_LIST['ENEMY']
                player.is_damaged = True

            pg.sprite.groupcollide(bluster_sprite_group, enemy_bluster_sprite_group, True, True)

            pg.sprite.groupcollide(antimatter_sprite_group, enemy_bluster_sprite_group, False, True)

            # Покраснение при попадании
            if player.is_damaged:
                cooldown_dmg = config.COOLDOWN_LIST['DMG']
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
            screen.blit(start, (config.WIDTH // 2 - 400, config.HEIGHT // 2 + 40 * i - 200))
        rec = END_FONT.render(f'Рекорд бесконечного режима: {record}', True, (200, 0, 255))
        screen.blit(rec, (100, config.HEIGHT - 100))


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
            create_particles(particles_sprite_group, config.GRAVITY, 1)
            particles_sprite_group.draw(screen)
            particles_sprite_group.update()

        end1 = END_FONT.render(end_message1, True, (255, 255, 255))
        end2 = END_FONT.render(end_message2, True, (255, 255, 255))
        end_scr = END_FONT.render(end_score, True, (255, 255, 255))

        screen.blit(end1, (config.WIDTH // 2 - 300, config.HEIGHT // 2 - 40))
        screen.blit(end2, (config.WIDTH // 2 - 300, config.HEIGHT // 2))
        screen.blit(end_scr, (config.WIDTH // 2 - 300, config.HEIGHT // 2 + 80))

        for i in btn_end:
            i.process(pos)


    # Начальный экран
    if is_start:
        if btn1.skip or btn2.skip or btn6.skip:
            is_start = False
        start()
        for btn in btns:
            btn.process(pos)

    # Конечный экран
    if is_end:
        win_score = config.WIN_SCORE_BASE
        end()

    # Отрисовка мыши
    if pg.mouse.get_focused() and show_mouse:
        arrow_sprite_group.update(pos)
        arrow_sprite_group.draw(screen)


    # Обновление параметров
    def update_all():
        clock.tick(config.FPS)
        pg.display.update()
        pg.display.flip()


    update_all()

    player.hp = max(0, player.hp)

pg.quit()
sys.exit()

import sys

import pygame as pg

import config
from ships_pews import (Arrow, EnemyShip, EnemyShipOmega, EnemyShipSpeed, load_image,
                        PewAntimatter, PewBase, PlayerShip, random_spawn)
from utils import (Button, create_particles, DataText, get_record_result,
                   write_record_result)


pg.init()
pg.display.set_caption(config.NAME)
pg.display.set_icon(load_image('player2.png'))
clock = pg.time.Clock()

screen = pg.display.set_mode((config.WIDTH, config.HEIGHT))
pg.mouse.set_visible(False)

BACKGROUND_IMAGE = pg.transform.scale(
    load_image('background2.png'), (config.WIDTH, config.HEIGHT))
BACKGROUND_START_IMAGE = pg.transform.scale(
    load_image('background3.png'), (config.WIDTH, config.HEIGHT))
BACKGROUND_END_IMAGE = pg.transform.scale(
    load_image('background4.png'), (config.WIDTH, config.HEIGHT))

FONT = pg.font.SysFont('Arial', 20)
MENU_FONT = pg.font.SysFont('Arial', 20)
END_FONT = pg.font.SysFont('Arial', 36)


class Game:
    def __init__(self):
        self.running = True
        self.debug_mode = config.DEBUG_SETTINGS
        self.record = get_record_result()

        self.player_sprite_group = pg.sprite.Group()
        self.arrow_sprite_group = pg.sprite.Group()
        self.particles_sprite_group = pg.sprite.Group()

        self.bluster_sprite_group = pg.sprite.Group()
        self.antimatter_sprite_group = pg.sprite.Group()
        self.enemy_bluster_sprite_group = pg.sprite.Group()
        self.enemy_ship_sprite_group = pg.sprite.Group()

        self.player = PlayerShip(self.player_sprite_group)
        self.arrow = Arrow(self.arrow_sprite_group)

        self.level = 1
        self.win_score = config.WIN_SCORE_BASE

        self.show_mouse = False
        self.is_start = True
        self.is_end = False
        self.play_music = True

        self.cooldown_base = 0
        self.cooldown_antimatter = 0
        self.cooldown_dmg = 10
        self.cooldown_enemy = 0

        self.theme_sound = pg.mixer.Sound('sound/main_music.mp3')
        self.pew_sound = pg.mixer.Sound('sound/pew.wav')
        self.pewantimatter_sound = pg.mixer.Sound('sound/antimatter.mp3')

        self.theme_sound.set_volume(0.1)
        self.pew_sound.set_volume(0.1)
        self.pewantimatter_sound.set_volume(0.1)

        self.btns = []
        self.btn_end = []
        self.init_buttons()

        self.TEXT = DataText(
            'start_text.txt',
            'end_text_good.txt',
            'end_text_bad.txt',
        )

        pass

    def init_buttons(self):
        self.btn1 = Button(config.WIDTH - 200, config.HEIGHT - 265, 150, 50,
                           screen, MENU_FONT, self.btns, 'Уровень 1', self.btn1_handler)
        self.btn2 = Button(config.WIDTH - 200, config.HEIGHT - 195, 150, 50,
                           screen, MENU_FONT, self.btns, 'Уровень 2', self.btn2_handler)
        self.btn6 = Button(config.WIDTH - 200, config.HEIGHT - 125, 150, 50,
                           screen, MENU_FONT, self.btns, 'Бесконечный',
                           self.btn6_handler)
        self.btn3 = Button(config.WIDTH - 200, config.HEIGHT - 55, 150, 50,
                           screen, MENU_FONT, self.btns, 'Выход', self.btn3_handler)
        self.btn7 = Button(10, config.HEIGHT - 60, 70, 50, screen,
                           MENU_FONT, self.btns, 'Музыка', self.btn7_handler)

        self.btn5 = Button(config.WIDTH // 2 - 250, config.HEIGHT - 150, 150,
                           50, screen, MENU_FONT, self.btn_end, 'Главная',
                           self.btn5_handler)
        self.btn4 = Button(config.WIDTH // 2 + 100, config.HEIGHT - 150, 150,
                           50, screen, MENU_FONT, self.btn_end, 'Выход',
                           self.btn3_handler)

    def run(self):
        self.theme_sound.play(-1)

        while self.running:
            is_gameplay = not (self.is_start or self.is_end)
            mouse_pos = pg.mouse.get_pos()
            self.show_mouse = False

            if self.player.score >= self.win_score or not self.player.is_alive():
                self.is_end = True

            if self.debug_mode:
                pg.display.set_caption(
                    config.NAME + ' | ' + str(clock.get_fps())[:4] +
                    f' FPS | LVL: {self.level} | WIN: {self.win_score} | [DEBUG]')

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        if is_gameplay:
                            self.btn5_handler(1)
                        else:
                            self.running = False
                    elif event.key == pg.K_SPACE:
                        if self.debug_mode:
                            if not self.is_end:
                                self.is_end = True
                                self.is_start = False
                            else:
                                self.is_end = False
                                self.is_start = True
                                self.btn5_handler(1)
                    elif event.key == pg.K_TAB:
                        if self.debug_mode:
                            self.debug_mode = False
                            pg.display.set_caption(config.NAME)
                        else:
                            self.debug_mode = True
                    elif event.key == pg.K_m:
                        self.btn7_handler(1)

                elif event.type == pg.MOUSEBUTTONDOWN:
                    if is_gameplay:
                        if event.button == 1:
                            if not self.cooldown_base and self.player.is_alive():
                                self.pew_sound.play()
                                PewBase(self.bluster_sprite_group, 4, 1, mouse_pos)
                                self.cooldown_base = config.COOLDOWN_LIST['BASE']
                        if event.button == 2:
                            if (not self.cooldown_base
                                    and self.player.is_alive()
                                    and self.debug_mode):
                                self.player.change_score(100)
                        elif event.button == 3:
                            if not self.cooldown_antimatter and not self.is_end:
                                self.pewantimatter_sound.play()
                                PewAntimatter(
                                    self.antimatter_sprite_group, 4, 1, mouse_pos)
                                self.cooldown_antimatter = (
                                    config.COOLDOWN_LIST)['ANTIMATTER']

            self.draw_background()

            if is_gameplay:
                self.main_part()
                self.cooldown_update()
                self.draw_all_sprites()
                if pg.mouse.get_focused():
                    self.update_all_sprites(mouse_pos)
                self.draw_info()

            if self.player.is_damaged:
                self.cooldown_dmg = config.COOLDOWN_LIST['DMG']
                self.player.is_damaged = False

            if not self.cooldown_dmg:
                self.player.image = self.player.default_image

            if self.is_start:
                if self.btn1.skip or self.btn2.skip or self.btn6.skip:
                    self.is_start = False
                self.start()
                for btn in self.btns:
                    btn.process(mouse_pos)

            if self.is_end:
                self.win_score = config.WIN_SCORE_BASE
                self.end(mouse_pos)

            if pg.mouse.get_focused() and self.show_mouse:
                self.arrow_sprite_group.update(mouse_pos)
                self.arrow_sprite_group.draw(screen)

            self.update_all()

    def draw_background(self):
        if self.is_start:
            screen.blit(BACKGROUND_START_IMAGE, (0, 0))
        elif self.is_end:
            screen.blit(BACKGROUND_END_IMAGE, (0, 0))
        else:
            screen.blit(BACKGROUND_IMAGE, (0, 0))

    def main_part(self):
        pg.event.set_grab(True)

        if pg.mouse.get_focused():
            if self.cooldown_enemy == 0:
                random_spawn(self.enemy_ship_sprite_group,
                             self.enemy_bluster_sprite_group, self.player, self.level)
                self.cooldown_enemy = config.COOLDOWN_LIST['ENEMY']

            hits = pg.sprite.groupcollide(
                self.enemy_ship_sprite_group, self.bluster_sprite_group, False, True)
            for hit in hits:
                if isinstance(hit, EnemyShip):
                    hit.image = hit.default_damaged_image
                    hit.hp = max(0, hit.hp - config.DAMAGE_LIST['BASE'])
                elif isinstance(hit, EnemyShipSpeed):
                    hit.image = hit.default_damaged_image
                    hit.hp = max(0, hit.hp - config.DAMAGE_LIST['BASE'])
                elif isinstance(hit, EnemyShipOmega):
                    hit.image = hit.default_damaged_image
                    hit.hp = max(0, hit.hp - config.DAMAGE_LIST['BASE'])

            hits = pg.sprite.groupcollide(
                self.enemy_ship_sprite_group, self.antimatter_sprite_group,
                False, False)
            for hit in hits:
                hit.image = hit.default_damaged_image
                hit.hp = max(0, hit.hp - config.DAMAGE_LIST['ANTIMATTER'])

            hits = pg.sprite.groupcollide(
                self.player_sprite_group, self.enemy_ship_sprite_group, False, True)
            for hit in hits:
                hit.hp -= config.DAMAGE_LIST['ENEMY']
                self.player.is_damaged = True

            pg.sprite.groupcollide(self.bluster_sprite_group,
                                   self.enemy_bluster_sprite_group, True, True)

            pg.sprite.groupcollide(self.antimatter_sprite_group,
                                   self.enemy_bluster_sprite_group, False, True)

    def draw_all_sprites(self):
        self.bluster_sprite_group.draw(screen)
        self.antimatter_sprite_group.draw(screen)
        self.enemy_bluster_sprite_group.draw(screen)
        self.player_sprite_group.draw(screen)
        self.enemy_ship_sprite_group.draw(screen)

    def update_all_sprites(self, pos: tuple[int, int]):
        self.bluster_sprite_group.update(pos)
        self.antimatter_sprite_group.update(pos)
        self.enemy_bluster_sprite_group.update(pos)
        self.enemy_ship_sprite_group.update(pos)
        self.player_sprite_group.update(pos)

    def draw_info(self):
        if self.cooldown_base:
            cooldown_blaster_info = FONT.render(
                f'Бластер: {self.cooldown_base}', True, (255, 0, 0))
        else:
            cooldown_blaster_info = FONT.render(
                'Бластер: ГОТОВ', True, (0, 255, 0))

        if self.cooldown_antimatter:
            cooldown_antimatter_info = FONT.render(
                f'Анти-материя: {self.cooldown_antimatter}', True, (255, 0, 0))
        else:
            cooldown_antimatter_info = FONT.render(
                'Анти-материя: ГОТОВ', True, (0, 255, 0))

        hp_status = FONT.render(f'ХП: {self.player.hp}', True, (200, 0, 255))
        score_status = FONT.render(f'Очки: {self.player.score}', True, (200, 0, 255))
        enemy_status = FONT.render(
            f'След. волна: {self.cooldown_enemy}', True, (200, 0, 255))
        lvl_status = FONT.render(f'Уровень: {self.level}', True, (200, 0, 255))

        screen.blit(hp_status, (10, 10))
        screen.blit(score_status, (100, 10))
        screen.blit(cooldown_blaster_info, (200, 10))
        screen.blit(cooldown_antimatter_info, (360, 10))
        screen.blit(enemy_status, (580, 10))
        screen.blit(lvl_status, (800, 10))

    def cooldown_update(self):
        if pg.mouse.get_focused():
            if self.cooldown_base:
                self.cooldown_base -= 1
            if self.cooldown_antimatter:
                self.cooldown_antimatter -= 1
            if self.cooldown_dmg:
                self.cooldown_dmg -= 1
            if self.cooldown_enemy:
                self.cooldown_enemy -= 1

    def start(self):
        self.show_mouse = True
        for i in range(len(self.TEXT.data_start)):
            start = END_FONT.render(self.TEXT.data_start[i], True, (255, 255, 255))
            screen.blit(start, (config.WIDTH // 2 - 400,
                        config.HEIGHT // 2 + 40 * i - 200))
        record_title = END_FONT.render(
            f'Рекорд бесконечного режима: {self.record}', True, (200, 0, 255))
        screen.blit(record_title, (100, config.HEIGHT - 100))

    def end(self, pos):
        pg.event.set_grab(False)
        self.show_mouse = True

        end_score = f'Всего очков: {self.player.score}'

        if not self.player.is_alive():
            end_message1 = self.TEXT.data_end2[0]
            end_message2 = self.TEXT.data_end2[1]
        else:
            end_message1 = self.TEXT.data_end1[0]
            end_message2 = self.TEXT.data_end1[1]
            create_particles(self.particles_sprite_group, config.GRAVITY, 1)
            self.particles_sprite_group.draw(screen)
            self.particles_sprite_group.update()

        end1 = END_FONT.render(end_message1, True, (255, 255, 255))
        end2 = END_FONT.render(end_message2, True, (255, 255, 255))
        end_scr = END_FONT.render(end_score, True, (255, 255, 255))

        screen.blit(end1, (config.WIDTH // 2 - 300, config.HEIGHT // 2 - 40))
        screen.blit(end2, (config.WIDTH // 2 - 300, config.HEIGHT // 2))
        screen.blit(end_scr, (config.WIDTH // 2 - 300, config.HEIGHT // 2 + 80))

        for i in self.btn_end:
            i.process(pos)

    def update_all(self):
        clock.tick(config.FPS)
        # pg.display.update()
        pg.display.flip()

    def btn1_handler(self, obj):
        self.level = 1
        obj.skip = True

    def btn2_handler(self, obj):
        self.level = 2
        obj.skip = True

    def btn3_handler(self, obj):
        if self.level == 3:
            write_record_result(self.player.score)
        self.record = get_record_result()
        self.running = False

    def btn5_handler(self, obj):
        for obj in self.bluster_sprite_group:
            obj.kill()
        for obj in self.antimatter_sprite_group:
            obj.kill()
        for obj in self.enemy_bluster_sprite_group:
            obj.kill()
        for obj in self.enemy_ship_sprite_group:
            obj.kill()

        self.cooldown_base = 0
        self.cooldown_antimatter = 0
        self.cooldown_dmg = 0
        self.cooldown_enemy = 50

        self.btn1.skip = False
        self.btn2.skip = False
        self.btn6.skip = False

        self.is_start = True
        self.is_end = False

        if self.level == 3:
            write_record_result(self.player.score)
        self.record = get_record_result()

        self.player = PlayerShip(self.player_sprite_group)

    def btn6_handler(self, obj):
        self.win_score = 999999
        self.level = 3
        obj.skip = True

    def btn7_handler(self, obj):
        self.play_music = not self.play_music
        self.theme_sound.set_volume(0.1 if self.play_music else 0)


def main():
    game = Game()
    game.run()

    pg.quit()
    sys.exit()


if __name__ == '__main__':
    main()

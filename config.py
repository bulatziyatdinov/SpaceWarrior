# Название
NAME = "Space Warrior"

# Debug
DEBUG_SETTINGS = True

# Размеры экрана
WIDTH = 1000
HEIGHT = 600

# ФПС
FPS = 60

# Очки для победы
WIN_SCORE_BASE = 100

# Шанс выстрела врага
ENEMY_FIRE_CHANCE = 100

# Здоровье игрока
PLAYER_HP = 100

# Гравитация
GRAVITY = 0.1

SPEED_SETTINGS = {
    'BASE_SPEED': 8,
    'ANTIMATTER_SPEED': 16,
    'ENEMY_SPEED': (2, 4),
}

COOLDOWN_LIST = {
    'BASE': 11,
    'ANTIMATTER': 80,
    'DMG': 14,
    'ENEMY': 200,
}

DAMAGE_LIST = {
    'BASE': 20,
    'ANTIMATTER': 8,
    'ENEMY': 10,
}

ENEMY_HP = {
    'BASE': 40,
    'OMEGA': 120,
}

LEVEL_CHANCHES = {
    1: (1, 1),
    2: (0, 6),
    3: (0, 3),
}

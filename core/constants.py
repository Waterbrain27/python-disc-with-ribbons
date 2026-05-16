"""Файл, содержащий константы для геометрии, генерации и GUI."""

import colorsys
import random

# Геометрия
DISK_RADIUS = 3.0
DISK_CENTER = (0, 0, 0)
DISK_THICKNESS = 0.0
DISK_COLOR = 'skyblue'
DISK_ALPHA = 0.6
PLANE_RADIUS = 3.0
PLANE_CENTER = [0, 0, 0]
PLANE_THICKNESS = 0.0
PLANE_ALPHA = 0.1
PERMISSIBLE_RANGE = 0.1

# Ленточки
MOVE_MARGIN = 2
RIBBON_DEFAULT_TWIST = 0
RIBBON_DEFAULT_THICKNESS = 0.0
RIBBON_COLOR = 'orange'
RIBBON_ALPHA = 0.8
RIBBON_RADIUS = 3.0
POINT_RADIUS = 0.052
POINT_COLOR = 'red'

# Генерация
MIN_WIDTH = 4
MIN_DELTA = 10          # минимальная длина дуги в градусах
MIN_INTERVAL_LENGTH = MIN_DELTA * 0.35
MAX_ATTEMPTS = 60

# Интерфейс
WINDOW_TITLE = "Disc with ribbons"
WINDOW_SIZE = (1520, 790)
BUTTON_FONT = "Arial"
BUTTON_SIZE = 16
TEXT_SIZE = 1
BASIC_TEXT_COLOR = 'black'

PALETTE = []
for i in range(360):
    hue = i / 360.0
    r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
    PALETTE.append((int(r*255), int(g*255), int(b*255)))
random.shuffle(PALETTE)
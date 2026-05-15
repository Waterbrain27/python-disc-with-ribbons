"""Геометрические вспомогательные функции для углов и точек."""

import numpy as np
import random
import math
from typing import List, Tuple, Union
from core.constants import MIN_INTERVAL_LENGTH, DISK_CENTER, PERMISSIBLE_RANGE, DISK_RADIUS
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.drawable.ribbon import Ribbon

def is_on_disc(point: Union[Tuple[float, float, float], np.ndarray], center: Tuple[float, float, float] = DISK_CENTER, radius: float=DISK_RADIUS, tolerance: float=PERMISSIBLE_RANGE) -> bool:
    """Проверяет, лежит ли точка на окружности диска (в пределах tolerance)."""
    dx = point[0] - center[0]
    dy = point[1] - center[1]
    dz = point[2] - center[2]
    dist_to_center = math.sqrt(dx*dx + dy*dy + dz*dz)
    return abs(dist_to_center - radius) <= tolerance

def canon_arc(angle1: float, angle2: float) -> Tuple[float, float, float]:
    """
    Каноническое представление дуги на окружности.

    Возвращает (start, end, length), где length <= 180° и
    start — меньший угол в каноническом интервале.
    """
    angle1 %= 360
    angle2 %= 360
    dist = (angle2 - angle1) % 360
    if dist <= 180:
        return angle1, angle2, dist
    else:
        return angle2, angle1, 360 - dist


def angle_in_interval(angle: float, interval: Tuple[float, float]) -> bool:
    """Проверить, лежит ли угол внутри интервала (включая концы)."""
    a, b = interval
    if a <= b:
        return a <= angle <= b
    else:
        return angle >= a or angle <= b


def angle_in_interval_strictly(angle: float, interval: Tuple[float, float]) -> bool:
    """Проверить, лежит ли угол строго внутри интервала (исключая концы)."""
    a, b = interval
    if a <= b:
        return a < angle < b
    else:
        return angle > a or angle < b


def angle_to_point(angle: float, radius: float, center: Tuple[float, float, float] = DISK_CENTER) -> np.ndarray:
    """Преобразовать угол на диске в 3D-точку (z = center[2])."""
    rad = np.radians(angle)
    return np.array([radius * np.cos(rad), radius * np.sin(rad), center[2]])


def point_to_angle(point: Union[Tuple[float, float, float], np.ndarray],
                    center: Tuple[float, float, float] = DISK_CENTER) -> float:
    """Преобразовать 3D-точку (игнорируя z) в угол в градусах [0, 360)."""
    dx = point[0] - center[0]
    dy = point[1] - center[1]
    return np.degrees(np.arctan2(dy, dx)) % 360


def rand_float(start: float, end: float) -> float:
    """Вернуть случайное число с плавающей точкой в [start, end]."""
    return random.random() * (end - start) + start


def rand_angle(interval: Tuple[float, float]) -> float:
    """
    Вернуть случайный угол внутри заданного интервала с учётом перехода через 360°.
    """
    start, end = interval
    if start < end:
        return rand_float(start, end)
    else:
        return random.choice([rand_float(start, 360.0), rand_float(0.0, end)])


def dist(interval: Tuple[float, float]) -> float:
    """Вернуть длину (в градусах) канонической дуги интервала."""
    _, _, delta = canon_arc(interval[0], interval[1])
    return delta

def almost_equal(a: float, b: float) -> bool:
    diff = abs(a - b) % 360
    return diff < 1e-3 or diff > 360 - 1e-3

def bool_canon(angle1: float, angle2: float) -> bool:
    start, end, _ = canon_arc(angle1, angle2)
    return almost_equal(start, angle1)


def form_free_room_list(intervals: List[tuple[tuple[float, float], 'Ribbon']]) -> List[List[float]]:
    """
    По заданному отсортированному списку занятых интервалов (список [start, end])
    вернуть список свободных интервалов, достаточно больших (длиннее MIN_INTERVAL_LENGTH).
    """
    free_room = []
    for i in range(len(intervals) - 1):
        start, end, d = canon_arc(intervals[i][0][1], intervals[i + 1][0][0])
        if d > MIN_INTERVAL_LENGTH:
            free_room.append([intervals[i][0][1], intervals[i + 1][0][0]])
    start, end, d = canon_arc(intervals[-1][0][1], intervals[0][0][0])
    if d > MIN_INTERVAL_LENGTH:
        free_room.append([intervals[-1][0][1], intervals[0][0][0]])
    return free_room
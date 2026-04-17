import numpy as np
import random
from core.constants import MIN_INTERVAL_LENGTH

def canon_arc(angle1, angle2):
    angle1 %= 360
    angle2 %= 360
    dist = (angle2 - angle1) % 360
    if dist <= 180:
        return angle1, angle2, dist
    else:
        return angle2, angle1, 360 - dist

def angle_in_interval(angle, interval):
    a, b = interval
    if a <= b:
        return a <= angle <= b
    else:
        return angle >= a or angle <= b

def angle_to_point(angle: float, radius: float, center=(0,0,0)) -> np.ndarray:
    rad = np.radians(angle)
    return np.array([radius * np.cos(rad), radius * np.sin(rad), center[2]])

def point_to_angle(point, center=(0,0,0)) -> float:
    dx = point[0] - center[0]
    dy = point[1] - center[1]
    return np.degrees(np.arctan2(dy, dx)) % 360

def rand_float(start : float, end : float) -> float:
    return random.random() * (end - start) + start

def rand_angle(interval):
    start = interval[0]
    end = interval[1]
    if start < end:
        return rand_float(start, end)
    else:
        return random.choice([rand_float(start, 360.0), rand_float(0.0, end)])

def dist(interval):
    start, end, delta = canon_arc(interval[0], interval[1])
    return delta

def form_free_room_list(intervals):
    free_room = []
    for i in range(len(intervals) - 1):
        start, end, dist = canon_arc(intervals[i][1], intervals[i + 1][0])
        if dist > MIN_INTERVAL_LENGTH:
            free_room.append([intervals[i][1], intervals[i + 1][0]])
    start, end, dist = canon_arc(intervals[-1][1], intervals[0][0])
    if dist > MIN_INTERVAL_LENGTH:
        free_room.append([intervals[-1][1], intervals[0][0]])
    return free_room
import vedo
import numpy as np
import random

MIN_DELTA = 20
MIN_INTERVAL_LENGTH = MIN_DELTA * 0.2
MIN_WIDTH = MIN_INTERVAL_LENGTH
MAX_WIDTH_RATIO = 0.4
MAX_ATTEMPTS = 60
disk_center = (0,0,0)
radius = 3.0
thickness = 0.1
disk = vedo.Circle(r=radius, res=120).extrude(zshift=thickness)
disk.c('skyblue').alpha(0.6)

rng = np.random.default_rng()

def canon_arc(angle1, angle2):
    angle1 %= 360
    angle2 %= 360
    dist = (angle2 - angle1) % 360
    if dist <= 180:
        return angle1, angle2, dist
    else:
        return angle2, angle1, 360 - dist

def dist(interval):
    start, end, delta = canon_arc(interval[0], interval[1])
    return delta

def angle_in_interval(angle, interval):
    a, b = interval
    if a <= b:
        return a <= angle <= b
    else:
        return angle >= a or angle <= b

# def is_arc_free(start, end):
#     arc_start, arc_end, delta = canon_arc(start, end)
#     if delta < 1e-6:
#         return False
#     for a, b in ribbons_coords:
#         if a <= b:
#             if not (arc_end <= a or arc_start >= b):
#                 return False
#         else:
#             if arc_end > a or arc_start < b:
#                 return False
#     return True

def create_arc(angle1, angle2, height_change):
    angle1 = np.radians(angle1)
    angle2 = np.radians(angle2)
    p1 = (radius * np.cos(angle1), radius * np.sin(angle1), 0)
    p2 = (radius * np.cos(angle2), radius * np.sin(angle2), 0)
    mid = (np.array(p1) + np.array(p2)) / 2
    vec = mid - np.array(disk_center)
    length = np.linalg.norm(vec)
    if length < 1e-9:
        vec = np.array([-mid[1], mid[0], 0])
        length = np.linalg.norm(vec)
    norm = vec / length
    arc_center = norm * radius + np.array([0.0, 0.0, height_change])
    arc_line = vedo.Arc(center=arc_center, point1=p1, point2=p2, res=50, invert=True)
    return arc_line

def create_ribbon(angle1, angle2, width):
    start, end, dist = canon_arc(angle1, angle2)
    if dist < 1e-6:
        print("You can't attach two edges to one point!")
        return None, start, end, width
    height_change = rand_float(-0.8, 0.8)
    outer_arc = create_arc(start, end, height_change)
    ratio = width / dist
    inner_start = (start + width) % 360
    inner_end = (end - width) % 360
    inner_arc = create_arc(inner_start, inner_end, height_change * (1 - 2 * ratio))
    ribbon_surface = vedo.Ribbon(outer_arc, inner_arc)
    ribbon = ribbon_surface.extrude(zshift=thickness, res=1)
    ribbon.c('orange').alpha(0.8)
    ribbons.append(ribbon)
    add_closed_intervals(start, end, width)
    return ribbon, start, end, width

all_heights = []
ribbons = []
ribbons_coords = []

def rand_float(start, end):
    return random.random() * (end - start) + start

def rand_angle(interval):
    start = interval[0]
    end = interval[1]
    if start < end:
        return rand_float(start, end)
    else:
        return random.choice([rand_float(start, 360.0), rand_float(0.0, end)])

def form_free_room_list(intervals):
    # normalized = []
    # for a, b in intervals:
    #     a = a % 360
    #     b = b % 360
    #     if a < b:
    #         normalized.append([a, b])
    #     elif a > b:
    #         normalized.append([a, 360.0])
    #         normalized.append([0.0, b])
    # if not normalized:
    #     return [[0.0, 360.0]]
    # normalized.sort(key=lambda x: x[0])
    # merged = [normalized[0]]
    # for a, b in normalized[1:]:
    #     if a <= merged[-1][1]:
    #         merged[-1][1] = max(merged[-1][1], b)
    #     else:
    #         merged.append([a, b])
    # free = []
    # for i in range(len(merged)):
    #     cur_end = merged[i][1]
    #     next_start = merged[(i + 1) % len(merged)][0]
    #     if i == len(merged) - 1:
    #         if cur_end < 360:
    #             free.append([cur_end, 360.0])
    #         if next_start > 0:
    #             free.append([0.0, next_start])
    #     else:
    #         if cur_end < next_start and next_start - cur_end > MIN_DELTA:
    #             free.append([cur_end, next_start])
    # return free
    free_room = []
    for i in range(len(intervals) - 1):
        start, end, dist = canon_arc(intervals[i][1], intervals[i + 1][0])
        if dist > MIN_INTERVAL_LENGTH:
            free_room.append([intervals[i][1], intervals[i + 1][0]])
    start, end, dist = canon_arc(intervals[-1][1], intervals[0][0])
    if dist > MIN_INTERVAL_LENGTH:
        free_room.append([intervals[-1][1], intervals[0][0]])
    return free_room


def add_closed_intervals(start, end, width):
    global ribbons_coords
    # start_start = start
    # start_end = (start + width) % 360
    # if start_start < start_end:
    #     ribbons_coords.append([start_start, start_end])
    # else:
    #     ribbons_coords.append([start_start, 360.0])
    #     ribbons_coords.append([0.0, start_end])
    # end_start = (end - width) % 360
    # end_end = end
    # if end_start < end_end:
    #     ribbons_coords.append([end_start, end_end])
    # else:
    #     ribbons_coords.append([end_start, 360.0])
    #     ribbons_coords.append([0.0, end_end])
    ribbons_coords.append([start, (start + width) % 360])
    ribbons_coords.append([(end - width) % 360, end])
    ribbons_coords = sorted(ribbons_coords, key=lambda x: x[0])

def generate_random_ribbon():
    global ribbons_coords
    sector = None
    if not ribbons_coords:
        for attempt in range(MAX_ATTEMPTS):
            angle1 = rand_float(0, 360)
            angle2 = rand_float(0, 360)
            start, end, delta = canon_arc(angle1, angle2)
            if delta >= MIN_DELTA:
                width = rand_float(delta * 0.1, delta * 0.2)
                create_ribbon(angle1, angle2, width)
                return
        print("Не удалось создать первую ленточку")
        return

    # Possibility to attach a ribbon to two different boundary circles

    free_room = form_free_room_list(ribbons_coords)
    if not free_room:
        print(f"Всё место занято, ленточки некуда ставить!")
        return
    one, two = rng.integers(0, len(free_room), 2)
    sector1 = free_room[one]
    sector2 = free_room[two]
    if one != two:
        min_range = min(dist(sector1), dist(sector2))
        if min_range < MIN_INTERVAL_LENGTH:
            print(f"Один из секторов - {min(sector1, sector2, key=lambda x: dist(x))} слишком узкий, пропускаем")
            return
        for attempt in range(MAX_ATTEMPTS):
            angle1 = rand_angle(sector1)
            angle2 = rand_angle(sector2)
            start, end, delta = canon_arc(angle1, angle2)
            # if not is_arc_free(start, end):
            #     continue
            if delta < MIN_DELTA:
                continue
            if angle_in_interval(start, sector1):
                start_sector, end_sector = sector1, sector2
            else:
                start_sector, end_sector = sector2, sector1
            max_width = min(dist([start_sector[1], start]), dist([end, end_sector[0]]))
            width = rand_float(max_width * 0.4, max_width * 0.8)
            result = create_ribbon(angle1, angle2, width)
            if result is not None:
                ribbon, s, e, w = result
                print(f"Создана ленточка: углы {s:.1f}°–{e:.1f}°, ширина {w:.1f}°, соотношение {w / delta:.2f}")
                return
    else:
        sector = sector1
        if dist(sector) < MIN_DELTA:
            print(f"Сектор {sector} слишком узкий, пропускаем")
            return
        for attempt in range(MAX_ATTEMPTS):
            angle1 = rand_angle(sector)
            angle2 = rand_angle(sector)
            start, end, delta = canon_arc(angle1, angle2)
            if delta < MIN_DELTA:
                continue
            width = rand_float(delta * 0.1, delta * 0.2)
            result = create_ribbon(angle1, angle2, width)
            if result is not None:
                ribbon, s, e, w = result
                print(f"Создана ленточка: углы {s:.1f}°–{e:.1f}°, ширина {w:.1f}°, соотношение {w / delta:.2f}")
                return
    if sector is not None:
        print(f"Не удалось сгенерировать ленточку в секторе {sector} за {MAX_ATTEMPTS} попыток")
    else:
        print(f"Не удалось сгенерировать ленточку (нет подходящих секторов)")


create_ribbon(20, 170, 10)

plt = vedo.Plotter(title="Диск с ленточками", size=(800, 500))

def add_random_ribbon(*args):
    old_count = len(ribbons)
    generate_random_ribbon()
    print('-----------------------------------------')
    print(ribbons_coords)
    print(form_free_room_list(ribbons_coords))
    if len(ribbons) > old_count:
        plt.add(ribbons[-1])
        plt.render()

plt.add_button(
    add_random_ribbon,
    pos=(0.5, 0.05),
    states=["Добавить ленточку"],
    c="orange",
    bc="green",
    font="Arial",
    size=16,
)

def show_free_room(*args):
    print('-----------------------------------')
    print(form_free_room_list(ribbons_coords))

plt.add_button(
    show_free_room,
    pos=(0.7, 0.05),
    c="darkgreen",
    bc="green",
    size=16
)

plt.add(disk)
for ribbon in ribbons:
    plt.add(ribbon)
plt.add(vedo.Rectangle((0, -0.05), (1, 0.05), res=12, c="red", alpha=1).extrude(zshift=thickness, res=1))

input_text = "Hello, world!"
text_display = vedo.Text2D(input_text, pos="top-left", font="Courier")

def keyboard_events(event):
    global input_text
    key = event.keypress
    if key == "Escape":
        plt.close()
    elif key == "BackSpace" and input_text:
        input_text = input_text[:-1]
    elif len(key) == 1:
        input_text += key
    text_display.text(input_text)
    plt.render()


plt.add_callback("key press", keyboard_events)
plt.add(text_display)
plt.show(axes=1, viewup='z', interactive=True)

import vedo
import numpy as np

MIN_DELTA = 20
MAX_ATTEMPTS = 40
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
    if width >= dist * 0.45:
        width = dist * 0.35
    if width <= dist * 0.05:
        width = dist * 0.15
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
    return rng.random() * (end - start) + start

def form_free_room_list(intervals):
    normalized = []
    for a, b in intervals:
        a = a % 360
        b = b % 360
        if a < b:
            normalized.append([a, b])
        elif a > b:
            normalized.append([a, 360.0])
            normalized.append([0.0, b])
    if not normalized:
        return [[0.0, 360.0]]
    normalized.sort(key=lambda x: x[0])
    merged = [normalized[0]]
    for a, b in normalized[1:]:
        if a <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    free = []
    for i in range(len(merged)):
        cur_end = merged[i][1]
        next_start = merged[(i + 1) % len(merged)][0]
        if i == len(merged) - 1:
            if cur_end < 360:
                free.append([cur_end, 360.0])
            if next_start > 0:
                free.append([0.0, next_start])
        else:
            if cur_end < next_start:
                free.append([cur_end, next_start])
    return free

def add_closed_intervals(start, end, width):
    global ribbons_coords
    start_start = start
    start_end = (start + width) % 360
    if start_start < start_end:
        ribbons_coords.append([start_start, start_end])
    else:
        ribbons_coords.append([start_start, 360.0])
        ribbons_coords.append([0.0, start_end])
    end_start = (end - width) % 360
    end_end = end
    if end_start < end_end:
        ribbons_coords.append([end_start, end_end])
    else:
        ribbons_coords.append([end_start, 360.0])
        ribbons_coords.append([0.0, end_end])
    ribbons_coords = sorted(ribbons_coords, key=lambda x: x[0])

def generate_random_ribbon():
    global ribbons_coords
    if not ribbons_coords:
        for attempt in range(MAX_ATTEMPTS):
            angle1 = rand_float(0, 360)
            angle2 = rand_float(0, 360)
            start, end, delta = canon_arc(angle1, angle2)
            if delta >= MIN_DELTA:
                width = rand_float(0, delta * 0.8)
                create_ribbon(angle1, angle2, width)
                return
        print("Не удалось создать первую ленточку")
        return

    # Possibility to attach a ribbon to two different boundary circles

    # free_room = form_free_room_list(ribbons_coords)
    # sector1 = rng.choice(free_room)
    # angle1 = rand_float(sector1[0], sector1[1])
    # angle1 %= 360
    # sector2 = rng.choice(free_room)
    # angle2 = rand_float(sector2[0], sector2[1])
    # angle2 %= 360
    # if sector1 != sector2:
    #     min_range = min(sector1[1] - sector1[0], sector2[1] - sector2[0])
    #     width = rand_float(0, min_range)
    #     ribbons.append(create_ribbon(angle1, angle2, width))
    # else:
    #     width = rand_float(0, canon_arc(angle1, angle2)[2]) / 2
    #     ribbons.append(create_ribbon(angle1, angle2, width))
    # ribbons_coords.append([canon_arc(angle1, angle2)[0], canon_arc(angle1, angle2)[0] + width])
    # ribbons_coords.append([canon_arc(angle1, angle2)[1] - width, canon_arc(angle1, angle2)[1]])
    # ribbons_coords = sorted(ribbons_coords, key=lambda x: x[0])
    # print(angle1, angle2, width)
    # return None

    # Only one boundary circle

    free_room = form_free_room_list(ribbons_coords)
    if not free_room:
        return
    sector = free_room[rng.integers(len(free_room))]
    if sector[1] - sector[0] < MIN_DELTA:
        print(f"Сектор {sector} слишком узкий, пропускаем")
        return
    for attempt in range(MAX_ATTEMPTS):
        angle1 = rand_float(sector[0], sector[1])
        angle2 = rand_float(sector[0], sector[1])
        start, end, delta = canon_arc(angle1, angle2)
        if delta >= MIN_DELTA:
            width = rand_float(0, delta * 0.8)
            result = create_ribbon(angle1, angle2, width)
            if result is not None:
                ribbon, s, e, w = result
                print(f"Создана ленточка: углы {s:.1f}°–{e:.1f}°, ширина {w:.1f}°, соотношение {w / delta:.2f}")
                return
    print(f"Не удалось сгенерировать ленточку в секторе {sector} за {MAX_ATTEMPTS} попыток")


create_ribbon(0, 170, 20)

plt = vedo.Plotter(title="Диск с ленточками", size=(800, 800))

def add_random_ribbon(*args):
    old_count = len(ribbons)
    generate_random_ribbon()
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

plt.add(disk)
for ribbon in ribbons:
    plt.add(ribbon)

plt.show(axes=1, viewup='z', interactive=True)

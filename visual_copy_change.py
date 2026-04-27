import vedo
import numpy as np
import random

# ========== Константы и глобальные переменные ==========
MIN_DELTA = 20
MIN_INTERVAL_LENGTH = MIN_DELTA * 0.2
MAX_ATTEMPTS = 60

disk_center = (0, 0, 0)
radius = 3.0
thickness = 0

# Глобальные списки
ribbons = []            # объекты ленточек (Mesh)
ribbon_points = []      # объекты сфер-точек (по 2 на ленточку)
ribbons_params = []     # параметры: (angle1, angle2, width, twist)
ribbons_coords = []     # занятые интервалы на окружности

rng = np.random.default_rng()

# ========== Вспомогательные функции ==========
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

def rand_float(start, end):
    return random.random() * (end - start) + start

def rand_angle(interval):
    start = interval[0]
    end = interval[1]
    if start < end:
        return rand_float(start, end)
    else:
        return random.choice([rand_float(start, 360.0), rand_float(0.0, end)])

# ========== Геометрические построения ==========
def create_arc(angle1, angle2, height_change):
    """Создаёт дугу (Arc) между двумя углами на окружности, приподнятую на height_change."""
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

def rebuild_ribbon(angle1, angle2, width, twist=0):
    """
    Создаёт ленточку и две точки-сферы.
    Возвращает (ribbon_mesh, [point1, point2]).
    """
    start, end, delta = canon_arc(angle1, angle2)
    if delta < 1e-6:
        return None, None

    # Для простоты height_change = 0, twist пока не используется визуально
    height_change = 0.0
    outer_arc = create_arc(start, end, height_change)
    ratio = width / delta if delta > 0 else 0
    inner_start = (start + width) % 360
    inner_end = (end - width) % 360
    inner_arc = create_arc(inner_start, inner_end, height_change * (1 - 2 * ratio))
    ribbon_surface = vedo.Ribbon(outer_arc, inner_arc)
    ribbon = ribbon_surface.extrude(zshift=thickness, res=1)
    ribbon.c('orange').alpha(0.8)

    # Точки на концах
    p1 = (radius * np.cos(np.radians(angle1)), radius * np.sin(np.radians(angle1)), 0)
    p2 = (radius * np.cos(np.radians(angle2)), radius * np.sin(np.radians(angle2)), 0)
    point1 = vedo.shapes.Sphere(pos=p1, r=0.026, c='red')
    point2 = vedo.shapes.Sphere(pos=p2, r=0.026, c='red')

    return ribbon, [point1, point2]

def rebuild_all_intervals():
    """Перестраивает ribbons_coords на основе текущих ленточек."""
    global ribbons_coords
    ribbons_coords = []
    for a1, a2, w, _ in ribbons_params:
        # Интервал, занятый первым концом (ширина ленточки)
        s1 = a1
        e1 = (a1 + w) % 360
        # Интервал, занятый вторым концом
        s2 = (a2 - w) % 360
        e2 = a2

        def add_interval(s, e):
            if s <= e:
                ribbons_coords.append([s, e])
            else:
                ribbons_coords.append([s, 360.0])
                ribbons_coords.append([0.0, e])

        add_interval(s1, e1)
        add_interval(s2, e2)

    ribbons_coords.sort(key=lambda x: x[0])

def replace_ribbon(idx, new_angle1, new_angle2):
    """Заменяет ленточку с индексом idx на новую с углами new_angle1, new_angle2."""
    global ribbons, ribbon_points, ribbons_params
    if idx >= len(ribbons):
        return
    a1, a2, width, twist = ribbons_params[idx]
    # Проверка, что новая дуга достаточно длинна для текущей ширины
    _, _, delta = canon_arc(new_angle1, new_angle2)
    if delta < width + 1e-6:
        return

    new_ribbon, new_points = rebuild_ribbon(new_angle1, new_angle2, width, twist)
    if new_ribbon is None:
        return

    # Удаляем старые объекты из сцены
    plt.remove(ribbons[idx])
    plt.remove(ribbon_points[2*idx])
    plt.remove(ribbon_points[2*idx+1])

    # Обновляем списки
    ribbons[idx] = new_ribbon
    ribbon_points[2*idx] = new_points[0]
    ribbon_points[2*idx+1] = new_points[1]
    ribbons_params[idx] = (new_angle1, new_angle2, width, twist)

    # Добавляем новые объекты
    plt.add(new_ribbon)
    plt.add(new_points[0])
    plt.add(new_points[1])

    rebuild_all_intervals()
    plt.render()

# ========== Создание ленточек (для начальной или случайной) ==========
def create_ribbon_and_add(angle1, angle2, width, twist=0):
    """
    Создаёт ленточку, точки, добавляет в глобальные списки и в сцену.
    Возвращает (ribbon, [point1, point2]).
    """
    ribbon, points = rebuild_ribbon(angle1, angle2, width, twist)
    if ribbon is None:
        return None, None
    ribbons.append(ribbon)
    ribbon_points.extend(points)
    ribbons_params.append((angle1, angle2, width, twist))
    rebuild_all_intervals()
    # Добавляем в сцену, если plt уже существует
    if 'plt' in globals() and plt:
        plt.add(ribbon)
        plt.add(points[0])
        plt.add(points[1])
    return ribbon, points

def generate_random_ribbon(*args):
    """Генерирует случайную ленточку, учитывая свободные интервалы."""
    global ribbons_coords
    # Если ещё нет ленточек – создаём первую без проверок
    if not ribbons_coords:
        for attempt in range(MAX_ATTEMPTS):
            angle1 = rand_float(0, 360)
            angle2 = rand_float(0, 360)
            _, _, delta = canon_arc(angle1, angle2)
            if delta >= MIN_DELTA:
                width = rand_float(delta * 0.1, delta * 0.2)
                create_ribbon_and_add(angle1, angle2, width)
                return
        # print("Не удалось создать первую ленточку")
        return

    # Получаем свободные сектора
    free_room = []
    if ribbons_coords:
        # Сортируем и сливаем интервалы (упрощённо: просто идём по отсортированным)
        intervals = sorted(ribbons_coords, key=lambda x: x[0])
        # Добавляем виртуальный интервал от последнего до 360 и от 0 до первого
        all_intervals = []
        for a, b in intervals:
            all_intervals.append([a, b])
        # Свободные промежутки
        prev_end = 0.0
        for a, b in all_intervals:
            if a > prev_end + MIN_INTERVAL_LENGTH:
                free_room.append([prev_end, a])
            prev_end = max(prev_end, b)
        if prev_end < 360 - MIN_INTERVAL_LENGTH:
            free_room.append([prev_end, 360.0])
        if free_room and free_room[0][0] > 0:
            # цикл замкнулся: между последним и первым
            last_end = free_room[-1][1] if free_room else 0
            if 360 - last_end > MIN_INTERVAL_LENGTH:
                pass  # уже учтено

    if not free_room:
        # print("Нет свободного места для новой ленточки")
        return

    # Выбираем два разных сектора (или один, если ленточка внутри сектора)
    if len(free_room) >= 2:
        idx1, idx2 = rng.integers(0, len(free_room), 2)
        if idx1 == idx2:
            idx2 = (idx2 + 1) % len(free_room)
        sector1 = free_room[idx1]
        sector2 = free_room[idx2]
    else:
        sector1 = free_room[0]
        sector2 = free_room[0]  # ленточка в одном секторе

    for attempt in range(MAX_ATTEMPTS):
        if sector1 is sector2:
            angle1 = rand_angle(sector1)
            angle2 = rand_angle(sector1)
        else:
            angle1 = rand_angle(sector1)
            angle2 = rand_angle(sector2)
        _, _, delta = canon_arc(angle1, angle2)
        if delta < MIN_DELTA:
            continue
        width = rand_float(delta * 0.1, delta * 0.2)
        create_ribbon_and_add(angle1, angle2, width)
        return
    # print("Не удалось создать ленточку после нескольких попыток")

# ========== Инициализация сцены ==========
disk = vedo.Circle(r=radius, res=1200).extrude(zshift=thickness)
disk.c('skyblue').alpha(0.6)

plt = vedo.Plotter(title="Диск с ленточками", size=(800, 500))

# Кнопка добавления случайной ленточки
plt.add_button(
    generate_random_ribbon,
    pos=(0.5, 0.05),
    states=["Добавить ленточку"],
    c="orange",
    bc="green",
    font="Arial",
    size=16,
)

# Кнопка для отладки (показывает свободные интервалы)
def show_free_room(*args):
    rebuild_all_intervals()
    # print("Занятые интервалы:", ribbons_coords)
    # Вычисление свободных для вывода
    free = []
    if ribbons_coords:
        intervals = sorted(ribbons_coords, key=lambda x: x[0])
        prev = 0.0
        for a, b in intervals:
            if a > prev:
                free.append([prev, a])
            prev = max(prev, b)
        if prev < 360:
            free.append([prev, 360])
    else:
        free.append([0, 360])
    # print("Свободные интервалы:", free)

plt.add_button(
    show_free_room,
    pos=(0.7, 0.05),
    c="darkgreen",
    bc="green",
    size=16
)

# Добавляем диск
plt.add(disk)

# ========== Обработка перетаскивания точек ==========
dragged_point = None
dragged_ribbon_idx = None
dragged_end = None

def on_mouse_click(evt):
    global dragged_point, dragged_ribbon_idx, dragged_end
    if evt.actor and evt.actor in ribbon_points:
        dragged_point = evt.actor
        # Находим индекс ленточки
        for i in range(len(ribbons)):
            if ribbon_points[2*i] is dragged_point:
                dragged_ribbon_idx = i
                dragged_end = 0
                break
            elif ribbon_points[2*i+1] is dragged_point:
                dragged_ribbon_idx = i
                dragged_end = 1
                break

def on_mouse_drag(evt):
    global dragged_point, dragged_ribbon_idx, dragged_end
    if dragged_point is None or dragged_ribbon_idx is None:
        return
    # Получаем 3D координаты под курсором (луч, пересекающий плоскость z=0)
    # Для простоты используем evt.picked3d; если None – игнорируем
    pos3d = evt.picked3d
    if pos3d is None:
        return
    dx = pos3d[0] - disk_center[0]
    dy = pos3d[1] - disk_center[1]
    angle = np.degrees(np.arctan2(dy, dx)) % 360

    a1, a2, width, twist = ribbons_params[dragged_ribbon_idx]
    if dragged_end == 0:
        new_a1 = angle
        new_a2 = a2
    else:
        new_a1 = a1
        new_a2 = angle
    # Проверяем, что дуга не стала слишком маленькой
    _, _, delta = canon_arc(new_a1, new_a2)
    if delta < width + 1e-6:
        return
    replace_ribbon(dragged_ribbon_idx, new_a1, new_a2)

def on_mouse_release(evt):
    global dragged_point, dragged_ribbon_idx, dragged_end
    dragged_point = None
    dragged_ribbon_idx = None
    dragged_end = None

plt.add_callback("mouse click", on_mouse_click)
plt.add_callback("mouse move", on_mouse_drag)
plt.add_callback("mouse right click", on_mouse_release)

# ========== Запуск с демонстрационной ленточкой ==========
# Создаём одну ленточку для примера
create_ribbon_and_add(20, 170, 10)

# Отображаем сцену
plt.show(axes=1, viewup='z', interactive=True)
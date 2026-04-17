import numpy as np
from core.geometry import canon_arc
from core.factory import ObjectFactory
from core.constants import MAX_ATTEMPTS, MIN_DELTA, MIN_INTERVAL_LENGTH
from core.geometry import rand_float, dist, form_free_room_list, rand_angle, angle_in_interval

class RibbonGenerator:
    def __init__(self, disc_radius=3.0, thickness=0.0):
        self.radius = disc_radius
        self.thickness = thickness
        self.factory = ObjectFactory()
        self.rng = np.random.default_rng()

    def generate_random_ribbon(self, interval_manager):
        free_room = form_free_room_list(interval_manager.occupied)
        if not free_room:
            return None
        sector = None
        if not free_room:
            for attempt in range(MAX_ATTEMPTS):
                angle1 = rand_float(0, 360)
                angle2 = rand_float(0, 360)
                start, end, delta = canon_arc(angle1, angle2)
                if delta >= MIN_DELTA:
                    width = rand_float(delta * 0.1, delta * 0.2)
                    return self.factory.create_ribbon(angle1, angle2, width, 0, self.radius, self.thickness)
            print("Не удалось создать первую ленточку")
            return None

        # Possibility to attach a ribbon to two different boundary circles

        if not free_room:
            print(f"Всё место занято, ленточки некуда ставить!")
            return None
        one, two = self.rng.integers(0, len(free_room), 2)
        sector1 = free_room[one]
        sector2 = free_room[two]
        if one != two:
            min_range = min(dist(sector1), dist(sector2))
            if min_range < MIN_INTERVAL_LENGTH:
                print(f"Один из секторов - {min(sector1, sector2, key=lambda x: dist(x))} слишком узкий, пропускаем")
                return None
            for attempt in range(MAX_ATTEMPTS):
                angle1 = rand_angle(sector1)
                angle2 = rand_angle(sector2)
                start, end, delta = canon_arc(angle1, angle2)
                if delta < MIN_DELTA:
                    continue
                if angle_in_interval(start, sector1):
                    start_sector, end_sector = sector1, sector2
                else:
                    start_sector, end_sector = sector2, sector1
                max_width = min(dist([start, start_sector[1]]), dist([end_sector[0], end]))
                width = rand_float(max_width * 0.4, max_width * 0.8)
                ribbon = self.factory.create_ribbon(angle1, angle2, width, 0, self.radius, self.thickness)
                if ribbon is not None:
                    print(f"Создана ленточка: углы {angle1:.1f}°–{angle2:.1f}°, ширина {width:.1f}°")
                    return ribbon
        else:
            sector = sector1
            if dist(sector) < MIN_DELTA:
                print(f"Сектор {sector} слишком узкий, пропускаем")
                return None
            for attempt in range(MAX_ATTEMPTS):
                angle1 = rand_angle(sector)
                angle2 = rand_angle(sector)
                start, end, delta = canon_arc(angle1, angle2)
                if delta < MIN_DELTA:
                    continue
                width = rand_float(delta * 0.1, delta * 0.2)
                ribbon = self.factory.create_ribbon(angle1, angle2, width, 0, self.radius, self.thickness)
                if ribbon is not None:
                    print(f"Создана ленточка: углы {angle1:.1f}°–{angle2:.1f}°, ширина {width:.1f}°")
                    return ribbon
        if sector is not None:
            print(f"Не удалось сгенерировать ленточку в секторе {sector} за {MAX_ATTEMPTS} попыток")
        else:
            print(f"Не удалось сгенерировать ленточку (нет подходящих секторов)")

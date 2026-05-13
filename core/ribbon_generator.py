import random
import numpy as np
from typing import Optional
from core.geometry import canon_arc, rand_float, dist, form_free_room_list, rand_angle, angle_in_interval
from core.factory import ObjectFactory
from core.constants import MAX_ATTEMPTS, MIN_DELTA, MIN_INTERVAL_LENGTH, DISK_RADIUS, DISK_THICKNESS


class RibbonGenerator:
    """Генератор случайных ленточек, помещающихся в свободные интервалы."""

    def __init__(self, disc_radius: float = DISK_RADIUS, thickness: float = DISK_THICKNESS) -> None:
        self.radius = disc_radius
        self.thickness = thickness
        self.factory = ObjectFactory()
        self.rng = np.random.default_rng()

    def generate_random_ribbon(self, ribbon_manager: 'RibbonManager') -> Optional['Ribbon']:
        """
        Сгенерировать случайную ленточку, которая помещается в свободные интервалы.

        Returns:
            Экземпляр Ribbon или None, если генерация не удалась.
        """
        if not ribbon_manager.occupied:
            for attempt in range(MAX_ATTEMPTS):
                angle1 = rand_float(0, 360)
                angle2 = rand_float(0, 360)
                _, _, delta = canon_arc(angle1, angle2)
                if delta >= MIN_DELTA:
                    width = rand_float(delta * 0.1, delta * 0.2)
                    twist = random.randint(0, 1)
                    return self.factory.create_ribbon(angle1, angle2, width, twist,
                                                      self.radius, self.thickness, True)
            return None

        free_room = form_free_room_list(ribbon_manager.occupied)
        if not free_room:
            print("Всё место занято, ленточки некуда ставить!")
            return None

        one, two = self.rng.integers(0, len(free_room), 2)
        sector1 = free_room[one]
        sector2 = free_room[two]

        if one != two:
            min_range = min(dist(sector1), dist(sector2))
            if min_range < MIN_INTERVAL_LENGTH:
                print(f"Один из секторов слишком узкий, пропускаем")
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
                max_width = min((start_sector[1] - start) % 360, (end - end_sector[0]) % 360)
                width = rand_float(max_width * 0.4, max_width * 0.8)
                twist = random.randint(0, 1)
                ribbon = self.factory.create_ribbon(angle1, angle2, width, twist,
                                                    self.radius, self.thickness, True)
                if ribbon is not None:
                    print(f"Создана ленточка: углы {angle1:.1f}°–{angle2:.1f}°, ширина {width:.1f}°")
                    return ribbon
        else:
            sector = sector1
            if dist(sector) < MIN_DELTA:
                print(f"Сектор слишком узкий, пропускаем")
                return None
            for attempt in range(MAX_ATTEMPTS):
                angle1 = rand_angle(sector)
                angle2 = rand_angle(sector)
                start, end, delta = canon_arc(angle1, angle2)
                if delta < MIN_DELTA:
                    continue
                width = rand_float(delta * 0.1, delta * 0.2)
                twist = random.randint(0, 1)
                ribbon = self.factory.create_ribbon(angle1, angle2, width, twist,
                                                    self.radius, self.thickness, True)
                if ribbon is not None:
                    print(f"Создана ленточка: углы {angle1:.1f}°–{angle2:.1f}°, ширина {width:.1f}°")
                    return ribbon
        if sector is not None:
            print(f"Не удалось сгенерировать ленточку в секторе {sector} за {MAX_ATTEMPTS} попыток")
        else:
            print(f"Не удалось сгенерировать ленточку (нет подходящих секторов)")
        return None
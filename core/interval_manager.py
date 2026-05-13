from typing import List
from core.geometry import canon_arc, angle_in_interval_strictly


class RibbonManager:
    """Управляет списком ленточек и занятыми интервалами на диске."""

    def __init__(self) -> None:
        self.ribbons: List['Ribbon'] = []          # все текущие ленточки
        self.occupied: List[List[float]] = []      # занятые угловые интервалы

    def add_ribbon(self, ribbon: 'Ribbon') -> None:
        """Добавить ленточку и обновить занятые интервалы."""
        self.ribbons.append(ribbon)
        self._recalculate_intervals()

    def replace_ribbon(self, old_ribbon: 'Ribbon', new_ribbon: 'Ribbon') -> None:
        """Заменить старую ленточку новой и обновить интервалы."""
        if old_ribbon in self.ribbons:
            idx = self.ribbons.index(old_ribbon)
            self.ribbons[idx] = new_ribbon
            self._recalculate_intervals()

    def _recalculate_intervals(self) -> None:
        """Пересчитать занятые интервалы по всем ленточкам."""
        self.occupied = []
        for r in self.ribbons:
            start, end, _ = canon_arc(r.start_angle, r.end_angle)
            self.occupied.append([start, (start + r.width) % 360])
            self.occupied.append([(end - r.width) % 360, end])
        self.occupied.sort(key=lambda x: x[0])

    def is_interval_free(self, angle1: float, angle2: float) -> bool:
        """
        Проверить, свободен ли интервал (angle1, angle2) от занятых интервалов.
        """
        for a, b in self.occupied:
            if (angle_in_interval_strictly(angle1, (a, b)) or
                    angle_in_interval_strictly(angle2, (a, b)) or
                    angle_in_interval_strictly(a, (angle1, angle2)) or
                    angle_in_interval_strictly(b, (angle1, angle2))):
                return False
        return True
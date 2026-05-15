from typing import List

from core.constants import MOVE_MARGIN
from core.math_machinery.geometry import canon_arc, angle_in_interval_strictly


class RibbonManager:
    """Управляет списком ленточек и занятыми интервалами на диске."""

    def __init__(self) -> None:
        self.ribbons: List['Ribbon'] = []          # все текущие ленточки
        self.occupied: List[tuple[tuple[float, float], 'Ribbon']] = []      # занятые угловые интервалы

    def add_ribbon(self, ribbon: 'Ribbon', index: int = None) -> None:
        """Добавить ленточку и обновить занятые интервалы."""
        if index is None:
            self.ribbons.append(ribbon)
        else:
            self.ribbons.insert(index, ribbon)
        self._recalculate_intervals()

    def replace_ribbon(self, old_ribbon: 'Ribbon', new_ribbon: 'Ribbon') -> None:
        """Заменить старую ленточку новой и обновить интервалы."""
        if old_ribbon in self.ribbons:
            if new_ribbon is not None:
                idx = self.ribbons.index(old_ribbon)
                self.ribbons[idx] = new_ribbon
            else:
                self.ribbons.remove(old_ribbon)
            self._recalculate_intervals()

    def _recalculate_intervals(self) -> None:
        """Пересчитать занятые интервалы по всем ленточкам."""
        self.occupied = []
        for r in self.ribbons:
            if r:
                start, end, _ = canon_arc(r.start_angle, r.end_angle)
                self.occupied.append(((start, (start + r.width) % 360), r))
                self.occupied.append((((end - r.width) % 360, end), r))
        self.occupied.sort(key=lambda x: x[0][0])

    def is_interval_free(self, angle1: float, angle2: float, extend: bool = False, ignore=None) -> bool:
        """
        Проверить, свободен ли интервал (angle1, angle2) от занятых интервалов.
        """
        ignore = set(ignore or [])
        margin = MOVE_MARGIN if extend else 0.0
        left = (angle1 - margin) % 360
        right = (angle2 + margin) % 360

        for (a, b), ribbon in self.occupied:
            if ribbon in ignore:
                continue
            if (angle_in_interval_strictly(left, (a, b)) or
                angle_in_interval_strictly(right, (a, b)) or
                angle_in_interval_strictly(a, (left, right)) or
                angle_in_interval_strictly(b, (left, right))):
                return False
        return True
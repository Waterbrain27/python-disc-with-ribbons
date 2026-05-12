from core.geometry import canon_arc, angle_in_interval_strictly, form_free_room_list


class RibbonManager:
    def __init__(self):
        self.ribbons = []
        self.occupied = []

    def add_ribbon(self, ribbon):
        self.ribbons.append(ribbon)
        self._recalculate_intervals()

    def replace_ribbon(self, old_ribbon, new_ribbon):
        if old_ribbon in self.ribbons:
            idx = self.ribbons.index(old_ribbon)
            self.ribbons[idx] = new_ribbon
            self._recalculate_intervals()

    def _recalculate_intervals(self):
        self.occupied = []
        for r in self.ribbons:
            start, end, _ = canon_arc(r.start_angle, r.end_angle)
            self.occupied.append([start, (start + r.width) % 360])
            self.occupied.append([(end - r.width) % 360, end])
        self.occupied.sort(key=lambda x: x[0])

    def is_interval_free(self, angle1: float, angle2: float) -> bool:
        for a, b in self.occupied:
            if (angle_in_interval_strictly(angle1, (a, b)) or
                    angle_in_interval_strictly(angle2, (a, b)) or
                    angle_in_interval_strictly(a, (angle1, angle2)) or
                    angle_in_interval_strictly(b, (angle1, angle2))):
                return False
        return True

    # def is_move_valid(self, old_ribbon, new_angle1, new_angle2):
    #     """
    #     Проверяет, можно ли переместить ленточку так, чтобы её новые интервалы
    #     не пересекались с другими ленточками.
    #     """
    #     start, end, delta = canon_arc(new_angle1 % 360, new_angle2 % 360)
    #     if delta < old_ribbon.width + 1e-6:
    #         return False
    #
    #     w = old_ribbon.width
    #     new_intervals = [
    #         [start, (start + w) % 360],
    #         [(end - w) % 360, end]
    #     ]
    #
    #     # Строим список занятых интервалов без учёта old_ribbon
    #     other_occupied = []
    #     for r in self.ribbons:
    #         if r is old_ribbon:
    #             continue
    #         s, e, _ = canon_arc(r.start_angle, r.end_angle)
    #         other_occupied.append([s, (s + r.width) % 360])
    #         other_occupied.append([(e - r.width) % 360, e])
    #
    #     free = form_free_room_list(other_occupied)
    #     start_accessible1 = 0
    #     end_accessible1 = 0
    #     start_accessible2 = 0
    #     end_accessible2 = 0
    #     for free_interval in free:
    #         if angle_in_interval(old_ribbon.start_angle + w, free_interval):
    #             start_accessible1, end_accessible1 = free_interval
    #         if angle_in_interval(old_ribbon.end_angle - w, free_interval):
    #             start_accessible2, end_accessible2 = free_interval
    #
    #     if angle_in_interval(new_angle1, [start_accessible1, end_accessible1]) and angle_in_interval(new_angle2, [start_accessible2, end_accessible2]):
    #         return True
    #     return False
    #     # Проверяем, что ни один из четырёх «углов» нового интервала не попадает в чужой
    #     # test_angles = [start, (start + w) % 360, (end - w) % 360, end]
    #     # for angle in test_angles:
    #     #     for occ in other_occupied:
    #     #         if angle_in_interval(angle, occ):
    #     #             return False
    #     # return True
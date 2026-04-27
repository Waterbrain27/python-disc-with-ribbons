from core.geometry import canon_arc

class RibbonManager:
    def __init__(self):
        self.ribbons = []      # список объектов Ribbon
        self.occupied = []     # остаётся для интервалов

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
from core.geometry import canon_arc


class IntervalManager:
    def __init__(self):
        self.occupied = []  # список [start, end]

    def update_from_ribbons(self, ribbon):
        start, end, _ = canon_arc(ribbon.start_angle, ribbon.end_angle)
        self.occupied.append([start, (start + ribbon.width) % 360])
        self.occupied.append([(end - ribbon.width) % 360, end])
        self.occupied = sorted(self.occupied, key=lambda x: x[0])

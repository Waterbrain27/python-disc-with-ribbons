class IntervalManager:
    def __init__(self):
        self.occupied = []  # список [start, end]

    def update_from_ribbons(self, ribbon):
        self.occupied.append([ribbon.start, (ribbon.start + ribbon.width) % 360])
        self.occupied.append([(ribbon.end - ribbon.width) % 360, ribbon.end])
        self.occupied = sorted(self.occupied, key=lambda x: x[0])

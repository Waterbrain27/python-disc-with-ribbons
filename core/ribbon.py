import vedo
import numpy as np
from core.interfaces import IDrawable
from core.geometry import canon_arc, angle_to_point, rand_float

disk_center = (0,0,0)

class Ribbon(IDrawable):
    def __init__(self, angle1: float, angle2: float, width: float, twist: int = 0,
                 radius: float = 3.0, thickness: float = 0.0):
        self._angle1 = angle1 % 360
        self._angle2 = angle2 % 360
        self._width = width
        self._twist = twist
        self.radius = radius
        self.thickness = thickness
        self._mesh = None
        self._points = []   # две сферы-точки
        self._build()
        print(f"Ribbon __init__: angles {angle1}, {angle2}, width {width}")  # отладка

    def _build(self):
        print("Ribbon._build() started")
        try:
            start, end, dist = canon_arc(self.angle1, self.angle2)
            if dist < 1e-6:
                print("You can't attach two edges to one point!")
                return
            height_change = rand_float(-0.8, 0.8)
            outer_arc = self._create_arc(start, end, height_change)
            ratio = self.width / dist
            inner_start = (start + self.width) % 360
            inner_end = (end - self.width) % 360
            inner_arc = self._create_arc(inner_start, inner_end, height_change * (1 - 2 * ratio))
            ribbon_surface = vedo.Ribbon(outer_arc, inner_arc)
            if ribbon_surface is None:
                print("ribbon_surface is None")
                return
            self._mesh = ribbon_surface.extrude(zshift=self.thickness, res=1)
            self._mesh.c('orange').alpha(0.8)

        # Точки на концах
            p1 = angle_to_point(self._angle1, self.radius)
            p2 = angle_to_point(self._angle2, self.radius)
            point1 = vedo.shapes.Sphere(pos=p1, r=0.026, c='red')
            point2 = vedo.shapes.Sphere(pos=p2, r=0.026, c='red')
            self._points = [point1, point2]
            if self._mesh is None:
                print("ERROR: self._mesh still None after _build()")
            else:
                print(f"_build() OK, mesh = {self._mesh}")
        except Exception as e:
            print(f"Exception in _build: {e}")

    def _create_arc(self, angle1, angle2, height_change):
        angle1 = np.radians(angle1)
        angle2 = np.radians(angle2)
        p1 = (self.radius * np.cos(angle1), self.radius * np.sin(angle1), 0)
        p2 = (self.radius * np.cos(angle2), self.radius * np.sin(angle2), 0)
        mid = (np.array(p1) + np.array(p2)) / 2
        vec = mid - np.array(disk_center)
        length = np.linalg.norm(vec)
        if length < 1e-9:
            vec = np.array([-mid[1], mid[0], 0])
            length = np.linalg.norm(vec)
        norm = vec / length
        arc_center = norm * self.radius + np.array([0.0, 0.0, height_change])
        arc_line = vedo.Arc(center=arc_center, point1=p1, point2=p2, res=50, invert=True)
        return arc_line

    def get_mesh(self):
        return self._mesh

    def get_points(self):
        return self._points

    def update_angle(self, end: int, new_angle: float) -> bool:
        """Обновить один конец (0 или 1) и перестроить ленточку."""
        if end == 0:
            self._angle1 = new_angle % 360
        else:
            self._angle2 = new_angle % 360
        # Проверка, что дуга не стала короче ширины
        _, _, delta = canon_arc(self._angle1, self._angle2)
        if delta < self._width + 1e-6:
            return False
        self._build()
        return True

    @property
    def angle1(self):
        return self._angle1
    @property
    def angle2(self):
        return self._angle2
    @property
    def width(self):
        return self._width
    @property
    def twist(self):
        return self._twist
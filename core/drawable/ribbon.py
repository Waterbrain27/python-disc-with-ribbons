import vedo
import numpy as np
from typing import List, Tuple, Optional

from core.constants import RIBBON_DEFAULT_TWIST, RIBBON_RADIUS, RIBBON_DEFAULT_THICKNESS, RIBBON_ALPHA, POINT_RADIUS, \
    RIBBON_COLOR, POINT_COLOR, DISK_CENTER
from core.interfaces import IDrawable
from core.geometry import canon_arc, angle_to_point, rand_float


class Ribbon(IDrawable):
    """Ленточка, прикреплённая к диску."""

    def __init__(
        self,
        angle1: float,
        angle2: float,
        width: float,
        twist: int = RIBBON_DEFAULT_TWIST,
        radius: float = RIBBON_RADIUS,
        thickness: float = RIBBON_DEFAULT_THICKNESS,
        random_height: bool = True,
        height: float = 0.0
    ) -> None:
        self._start_angle = angle1 % 360
        self._end_angle = angle2 % 360
        self._width = width
        self._height = height
        self._random_height = random_height
        self._twist = twist
        self.radius = radius
        self.thickness = thickness
        self._mesh: Optional[vedo.Mesh] = None
        self.arcs: List[vedo.Arc] = []
        self._points: List[vedo.Sphere] = []   # две сферические метки на концах
        self._build()

    def _build(self) -> None:
        """Построить mesh ленточки, дуги и конечные сферы."""
        start, end, dist_ = canon_arc(self.start_angle, self.end_angle)
        if dist_ < 1e-6:
            print("Нельзя прикрепить два конца в одну точку!")
            return

        if self._random_height:
            self._height = rand_float(0.05, 1)

        ratio = self.width / dist_
        inner_start = (start + self.width) % 360
        inner_end = (end - self.width) % 360

        if not self._twist:
            outer_arc = self._create_arc(start, end, self._height)
            inner_arc = self._create_arc(inner_start, inner_end, self._height * (1 - 2 * ratio))
        else:
            outer_arc = self._create_arc(inner_start, end, self._height)
            inner_arc = self._create_arc(start, inner_end, self._height * (1 - 2 * ratio))

        self.arcs = [outer_arc, inner_arc]
        ribbon_surface = vedo.Ribbon(outer_arc, inner_arc)
        self._mesh = ribbon_surface.extrude(zshift=self.thickness, res=1)
        self._mesh.c(RIBBON_COLOR).alpha(RIBBON_ALPHA)

        # Конечные сферы
        p1 = angle_to_point(self._start_angle, self.radius)
        p2 = angle_to_point(self._end_angle, self.radius)
        point1 = vedo.shapes.Sphere(pos=p1, r=POINT_RADIUS, c=POINT_COLOR)
        point2 = vedo.shapes.Sphere(pos=p2, r=POINT_RADIUS, c=POINT_COLOR)
        self._points = [point1, point2]

    def _create_arc(self, angle1: float, angle2: float, height_change: float, c: str = RIBBON_COLOR) -> vedo.Arc:
        """Создать 3D-дугу между двумя углами, поднятую на height_change."""
        angle1_rad = np.radians(angle1)
        angle2_rad = np.radians(angle2)
        p1 = (self.radius * np.cos(angle1_rad), self.radius * np.sin(angle1_rad), 0)
        p2 = (self.radius * np.cos(angle2_rad), self.radius * np.sin(angle2_rad), 0)
        mid = (np.array(p1) + np.array(p2)) / 2
        vec = mid - np.array(DISK_CENTER)
        length = np.linalg.norm(vec)
        if length < 1e-9:
            vec = np.array([-mid[1], mid[0], 0])
            length = np.linalg.norm(vec)
        norm = vec / length
        arc_center = norm * self.radius + np.array([0.0, 0.0, height_change])
        arc_line = vedo.Arc(center=arc_center, point1=p1, point2=p2, res=50, invert=True)
        arc_line.c(c).lw(3)
        return arc_line

    def get_mesh(self) -> Optional[vedo.Mesh]:
        return self._mesh

    def get_arcs(self) -> List[vedo.Arc]:
        return self.arcs

    def get_points(self) -> List[vedo.Sphere]:
        return self._points

    def update_angle(self, end: int, new_angle: float) -> bool:
        """
        Обновить один конец ленточки и перестроить.

        Args:
            end: 0 для начала, 1 для конца.
            new_angle: новый угол в градусах.

        Returns:
            True в случае успеха, False если дуга становится слишком короткой.
        """
        if end == 0:
            self._start_angle = new_angle % 360
        else:
            self._end_angle = new_angle % 360
        _, _, delta = canon_arc(self._start_angle, self._end_angle)
        if delta < self._width + 1e-6:
            return False
        self._build()
        return True

    def clone_with_angles(self, new_angle1: float, new_angle2: float, twist: int = 0) -> Optional['Ribbon']:
        """
        Создать новую ленточку с заданными углами (если дуга достаточно длинна).

        Returns:
            Новая ленточка или None, если дуга слишком коротка.
        """
        _, _, delta = canon_arc(new_angle1, new_angle2)
        if delta < self._width * 2 + 1e-6:
            return None
        return Ribbon(new_angle1, new_angle2, self._width, twist,
                      self.radius, self.thickness, False, self._height)

    @property
    def start_angle(self) -> float:
        return self._start_angle

    @property
    def end_angle(self) -> float:
        return self._end_angle

    @property
    def width(self) -> float:
        return self._width

    @property
    def twist(self) -> int:
        return self._twist

    @property
    def height(self) -> float:
        return self._height
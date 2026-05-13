import vedo
import numpy as np

from core.constants import DISK_RADIUS, DISK_THICKNESS, PLANE_RADIUS, PLANE_THICKNESS, PLANE_CENTER, PLANE_ALPHA
from core.interfaces import IDrawable


class Plane(IDrawable):
    """Прозрачная плоскость под диском для визуальной справки."""

    def __init__(self, radius: float = PLANE_RADIUS, center: np.ndarray = np.array(PLANE_CENTER), thickness: float = PLANE_THICKNESS) -> None:
        self.radius = radius
        self.center = center
        self.thickness = thickness
        self._mesh: vedo.Mesh = None
        self._build()

    def _build(self) -> None:
        """Создать большую прозрачную плоскость."""
        plane = vedo.Rectangle(p1=(-self.radius * 2, -self.radius * 2, 0),
                               p2=(self.radius * 2, self.radius * 2, 0),
                               res=1200)
        self._mesh = plane.extrude(zshift=self.thickness)
        self._mesh.c('white').alpha(PLANE_ALPHA)

    def get_mesh(self) -> vedo.Mesh:
        return self._mesh
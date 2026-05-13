import vedo
from core.interfaces import IDrawable


class Disc(IDrawable):
    """3D-представление диска."""

    def __init__(self, radius: float = 3.0, center: tuple = (0, 0, 0), thickness: float = 0.0) -> None:
        self.radius = radius
        self.center = center
        self.thickness = thickness
        self._mesh: vedo.Mesh = None
        self._build()

    def _build(self) -> None:
        """Создать mesh диска (выдавленный круг)."""
        circle = vedo.Circle(r=self.radius, res=1200)
        self._mesh = circle.extrude(zshift=self.thickness)
        self._mesh.c('skyblue').alpha(0.6)

    def get_mesh(self) -> vedo.Mesh:
        return self._mesh
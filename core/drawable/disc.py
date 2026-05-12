import vedo
from core.interfaces import IDrawable

class Disc(IDrawable):
    def __init__(self, radius=3.0, center=(0,0,0), thickness=0.0):
        self.radius = radius
        self.center = center
        self.thickness = thickness
        self._mesh = None
        self._build()

    def _build(self):
        circle = vedo.Circle(r=self.radius, res=1200)
        self._mesh = circle.extrude(zshift=self.thickness)
        self._mesh.c('skyblue').alpha(0.6)

    def get_mesh(self):
        return self._mesh
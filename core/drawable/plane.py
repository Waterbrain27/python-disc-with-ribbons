import vedo
import numpy as np
from core.interfaces import IDrawable

class Plane(IDrawable):
    def __init__(self, radius=3.0, center=np.array([0, 0, 0]), thickness=0.0):
        self.radius = radius
        self.center = center
        self.thickness = thickness
        self._mesh = None
        self._build()

    def _build(self):
        plane = vedo.Rectangle(p1=(-self.radius * 2, -self.radius * 2, 0), p2=(self.radius * 2, self.radius * 2, 0), res=1200)
        self._mesh = plane.extrude(zshift=self.thickness)
        self._mesh.c('white').alpha(0.1)

    def get_mesh(self):
        return self._mesh
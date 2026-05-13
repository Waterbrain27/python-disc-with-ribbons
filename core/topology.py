from abc import ABC
from typing import List, Tuple

from core.boundary_graph import BoundaryGraph
from core.interfaces import ITopologyCalculator
from core.drawable.ribbon import Ribbon

class Topology(ITopologyCalculator, ABC):
    def __init__(self, ribbons=None):
        self.ribbons = ribbons
        self.g = 0 #количество ручек/род
        self.h = 0 #количество краевых окружностей/дырок
        self.m = 0 #количество лент Мебиуса
        self.k = 0 #количество ленточек
        self.is_orientable = True #ориентируемость поверхности
        self.chi = 0 #Эйлерова характеристика поверхности

    def compute(self):
        self.ribbon_count()
        self.boundary_count()
        self.genus()
        self._is_orientable()
        self.euler_characteristic()

    def ribbon_count(self):
        l = sum(1 for r in self.ribbons if r.twist == 0)
        self.m = sum(1 for r in self.ribbons if r.twist == 1)
        self.k = l + self.m

    def boundary_count(self):
        graph = BoundaryGraph(self.ribbons)
        graph.build()
        cycles = graph.get_cycles()
        self.h = len(cycles)

    def genus(self):
        self.g = (self.k - self.m + self.h + 1) // 2

    def _is_orientable(self):
        if self.m > 0:
            self.is_orientable = False
        else:
            self.is_orientable = True

    def euler_characteristic(self):
        if self.is_orientable:
            self.chi = 2 - 2 * self.g - self.h
        else:
            self.chi = 2 - self.m - self.h
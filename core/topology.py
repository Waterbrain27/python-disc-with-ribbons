from abc import ABC
from typing import List, Optional
from core.boundary_graph import BoundaryGraph
from core.interfaces import ITopologyCalculator
from core.drawable.ribbon import Ribbon


class Topology(ITopologyCalculator, ABC):
    """Вычислитель топологических инвариантов поверхности, образованной ленточками."""

    def __init__(self, ribbons: Optional[List[Ribbon]] = None) -> None:
        self.ribbons = ribbons
        self.g: int = 0          # род (количество ручек)
        self.h: int = 0          # количество краевых окружностей (дырок)
        self.m: int = 0          # количество лент Мёбиуса
        self.k: int = 0          # общее количество ленточек
        self.is_orientable: bool = True
        self.chi: int = 0        # эйлерова характеристика

    def compute(self) -> None:
        """Вычислить все топологические инварианты."""
        self.ribbon_count()
        self.boundary_count()
        self.genus()
        self._is_orientable()
        self.euler_characteristic()

    def ribbon_count(self) -> None:
        """Подсчитать количество неперекрученных (l) и перекрученных (m) ленточек."""
        l = sum(1 for r in self.ribbons if r.twist == 0)
        self.m = sum(1 for r in self.ribbons if r.twist == 1)
        self.k = l + self.m

    def boundary_count(self) -> None:
        """Подсчитать граничные циклы с помощью BoundaryGraph."""
        if not self.ribbons:
            self.h = 0
            return
        graph = BoundaryGraph(self.ribbons)
        graph.build()
        cycles = graph.get_cycles()
        self.h = len(cycles)

    def genus(self) -> None:
        """Вычислить род g по формуле: (k - m + h + 1) // 2."""
        self.g = (self.k - self.m + self.h + 1) // 2

    def _is_orientable(self) -> None:
        """Ориентируемость: false, если есть хотя бы одна лента Мёбиуса."""
        self.is_orientable = (self.m == 0)

    def euler_characteristic(self) -> None:
        """Вычислить эйлерову характеристику χ."""
        if self.is_orientable:
            self.chi = 2 - 2 * self.g - self.h
        else:
            self.chi = 2 - self.m - self.h
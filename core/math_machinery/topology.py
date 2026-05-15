from abc import ABC
from typing import List, Optional
from core.math_machinery.boundary_graph import BoundaryGraph
from core.managers.interfaces import ITopologyCalculator
from core.drawable.ribbon import Ribbon


class Topology(ITopologyCalculator, ABC):
    """Вычислитель топологических инвариантов поверхности, образованной ленточками."""

    def __init__(self, ribbons: Optional[List[Ribbon]] = None) -> None:
        self.ribbons = ribbons or []

        self.g: int = 0          # род (если поверхность ориентируема)
        self.h: int = 0          # количество краевых компонент
        self.m: int = 0          # количество плёнок Мёбиуса / crosscaps
        self.k: int = 0          # общее количество ленточек
        self.is_orientable: bool = True
        self.chi: int = 0        # эйлерова характеристика

        # служебные счётчики ленточек
        self.l: int = 0          # число неперекрученных ленточек
        self._twisted_count: int = 0   # число перекрученных ленточек

    def compute(self) -> None:
        """
        Вычислить все топологические инварианты.

        Порядок важен:
        1) считаем ленточки,
        2) считаем число граничных компонент,
        3) определяем ориентируемость,
        4) считаем χ,
        5) по χ, h и ориентируемости получаем g и m.
        """
        self.ribbon_count()
        self.boundary_count()
        self._is_orientable()
        self.euler_characteristic()
        self.genus()

    def ribbon_count(self) -> None:
        """
        Подсчитать количество неперекрученных и перекрученных ленточек.

        Важно: число перекрученных ленточек НЕ равно числу плёнок Мёбиуса поверхности,
        поэтому здесь self.m не трогаем.
        """
        self.k = len(self.ribbons)
        self.l = sum(1 for r in self.ribbons if r and r.twist == 0)
        self._twisted_count = sum(1 for r in self.ribbons if r and r.twist == 1)

    def boundary_count(self) -> None:
        """Подсчитать число граничных компонент с помощью BoundaryGraph."""
        if not self.ribbons:
            # пустая конфигурация = диск, у него одна граница
            self.h = 1
            return

        graph = BoundaryGraph(self.ribbons)
        graph.build()
        cycles = graph.get_cycles()
        self.h = len(cycles)

    def _is_orientable(self) -> None:
        """
        Поверхность ориентируема тогда и только тогда,
        когда все ленточки неперекрученные.
        """
        self.is_orientable = (self._twisted_count == 0)

    def euler_characteristic(self) -> None:
        """
        Эйлерова характеристика поверхности, полученной из диска
        приклеиванием k ленточек:

            χ = 1 - k

        потому что диск даёт одну 0-клетку, а каждая ленточка — одну 1-ручку.
        """
        self.chi = 1 - self.k

    def genus(self) -> None:
        """
        Вычислить g и m из χ, h и ориентируемости.

        Если поверхность ориентируема:
            χ = 2 - 2g - h
            g = (2 - h - χ) / 2
            m = 0

        Если поверхность неориентируема:
            χ = 2 - m - h
            m = 2 - h - χ
            g = 0
        """
        if self.is_orientable:
            self.m = 0
            self.g = (2 - self.h - self.chi) // 2
        else:
            self.g = 0
            self.m = 2 - self.h - self.chi

    def surface_type(self) -> str:
        """
        Возвращает строковое имя типа поверхности на основе вычисленных инвариантов.

        Returns:
            Название поверхности (например, "Disk", "Möbius strip", "Klein bottle with a hole", etc.)
        """

        if self.is_orientable:
            if self.h == 1:
                if self.g == 0:
                    return "Disk"
                elif self.g == 1:
                    return "Torus with a hole (sphere with one handle and two hole)"
                else:
                    return f"Sphere with {self.g} handles and one hole"
            elif self.h == 2:
                if self.g == 0:
                    return "Annulus (cylinder)"
                else:
                    return f"Sphere with {self.g} handles and two holes"
            else:
                return f"Sphere with {self.g} handles and {self.h} holes"
        else:
            if self.h == 1:
                if self.m == 1:
                    return "Möbius strip"
                elif self.m == 2:
                    return "Klein bottle with a hole (projective plane with a hole)"
                else:
                    return f"Sphere with {self.m} crosscaps and one hole"
            else:
                return f"Non-orientable surface with {self.h} boundaries and {self.m} crosscaps"
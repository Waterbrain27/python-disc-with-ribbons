"""Основной класс приложения, управляющий сценой, ленточками и взаимодействиями."""

import time
from typing import List, Optional, Any

import vedo

from core.math_machinery.boundary_graph import BoundaryGraph
from core.drawable.disc import Disc
from core.managers.factory import ObjectFactory
from core.drawable.plane import Plane
from core.math_machinery.geometry import angle_to_point, canon_arc
from core.managers.ribbon_generator import RibbonGenerator
from gui.vedo_renderer import VedoRenderer
from core.math_machinery.topology import Topology
from core.constants import DISK_RADIUS, PALETTE
from core.managers.interval_manager import RibbonManager
from gui.mouse_handler import MouseHandler


class Application:
    """
    Главный класс приложения.
    Управляет рендерером, диском, ленточками, их генерацией,
    обработкой событий мыши и отображением топологии.
    """

    def __init__(
        self,
        renderer: Optional[VedoRenderer] = None,
        disc_radius: float = DISK_RADIUS
    ) -> None:
        """
        Инициализация приложения.

        Args:
            renderer: экземпляр рендерера (если None, будет создан VedoRenderer).
            disc_radius: радиус диска.
        """
        self.renderer = renderer or VedoRenderer()
        self.disc_radius = disc_radius
        self.disc = Disc(radius=disc_radius)
        self.plane = Plane(radius=disc_radius)
        self.factory = ObjectFactory()
        self.ribbon_gen = RibbonGenerator(disc_radius)
        self.ribbon_manager = RibbonManager()
        self.topology_calc = Topology(self.ribbon_manager.ribbons)

        # Обработчик мыши
        self.mouse_handler = MouseHandler(
            get_ribbons_func=lambda: self.ribbon_manager.ribbons,
            disc_radius=disc_radius
        )
        self.mouse_handler.on_ribbon_updated = self._on_ribbon_changed

        # Флаги и служебные переменные
        self._adding_ribbon: bool = False
        self._last_add_time: float = 0.0

        # Дуги границы, отрисованные на сцене
        self.boundary_arcs: List[vedo.Arc] = []

    def init(self) -> None:
        """Инициализирует сцену: добавляет диск, плоскость, привязывает обработчики."""
        self.renderer.add_drawable(self.disc)
        self.renderer.add_drawable(self.plane)

        self.mouse_handler.attach(self.renderer)
        self.renderer.bind_key(self.on_key_press)
        self.renderer.add_text(
            "Space - add a ribbon",
            position="bottom-left",
            key="hint"
        )

    def on_key_press(self, evt: Any) -> None:
        """
        Обработчик нажатия клавиш.

        Args:
            evt: объект события vedo, содержащий поле keypress.
        """
        if evt.keypress == "space":
            self.add_random_ribbon()

    def add_random_ribbon(self, *args, **kwargs) -> None:
        """
        Генерирует и добавляет случайную ленточку, если это возможно.
        Защита от повторных вызовов и слишком частых добавлений.
        """
        if self._adding_ribbon:
            return
        now = time.time()
        if now - self._last_add_time < 0.5:   # защита от частых кликов
            return

        self._adding_ribbon = True
        self._last_add_time = now

        try:
            new_ribbon = self.ribbon_gen.generate_random_ribbon(self.ribbon_manager)
            if new_ribbon:
                self.ribbon_manager.add_ribbon(new_ribbon)
                self.renderer.add_drawable(new_ribbon)
                self._update_boundary()
                self._update_topology()
        except Exception as e:
            print(f"Ошибка при добавлении ленточки: {e}")
        finally:
            self._adding_ribbon = False

    def _update_boundary(self) -> None:
        """
        Перерисовывает граничные циклы на основе текущих ленточек.
        Удаляет старые дуги и создаёт новые, окрашенные в цвета палитры.
        """
        # Удалить старые дуги
        for arc in self.boundary_arcs:
            self.renderer.plotter.remove(arc)
        self.boundary_arcs.clear()

        ribbons = self.ribbon_manager.ribbons
        if not ribbons:
            return

        graph = BoundaryGraph(ribbons)
        graph.build()
        disk_edges_set = set(graph.disk_edges)
        cycles = graph.get_cycles()
        print(len(cycles))
        print(cycles)

        colors = PALETTE
        for i, cycle in enumerate(cycles):
            color = colors[i % len(colors)]
            for v1, v2, typ in cycle:
                if typ == 'disk':
                    p1 = angle_to_point(v1, DISK_RADIUS)
                    p2 = angle_to_point(v2, DISK_RADIUS)
                    raw = (v2 - v1) % 360
                    forward = (v1, v2) in disk_edges_set
                    invert = raw > 180 if forward else raw < 180
                    arc = vedo.Arc(
                        center=(0, 0, 0),
                        point1=p1,
                        point2=p2,
                        invert=invert,
                        res=100
                    )
                    arc.c(color).lw(4)
                    self.renderer.plotter.add(arc)
                    self.boundary_arcs.append(arc)
                elif typ == 'outer':
                    # Перекрасить внешний край ленточки
                    start, end, _ = canon_arc(v1, v2)
                    old_ribbon = graph.ribbon_outer[(start, end)]
                    idx = self.ribbon_manager.ribbons.index(old_ribbon)
                    self.ribbon_manager.ribbons[idx].arcs[0].c(color)
                else:  # typ == 'inner'
                    # Перекрасить внутренний край ленточки
                    start, end, _ = canon_arc(v1, v2)
                    old_ribbon = graph.ribbon_inner[(start, end)]
                    idx = self.ribbon_manager.ribbons.index(old_ribbon)
                    self.ribbon_manager.ribbons[idx].arcs[1].c(color)

        self.renderer.render()

    def _on_ribbon_changed(self, old_ribbon: 'Ribbon', new_ribbon: 'Ribbon') -> None:
        """
        Обратный вызов при изменении ленточки (перемещение конца или перекручивание).

        Args:
            old_ribbon: старая (заменяемая) ленточка.
            new_ribbon: новая ленточка.
        """
        self.ribbon_manager.replace_ribbon(old_ribbon, new_ribbon)
        self._update_boundary()
        self._update_topology()

    def _update_topology(self) -> None:
        """
        Вычисляет и отображает текущие топологические характеристики поверхности
        (ориентируемость, g, h, m, χ).
        """
        self.topology_calc.ribbons = self.ribbon_manager.ribbons
        self.topology_calc.compute()
        text = (
            f"{'orientable' if self.topology_calc.is_orientable else 'non-orientable'}, "
            f"g = {self.topology_calc.g}, "
            f"h = {self.topology_calc.h}, "
            f"m = {self.topology_calc.m}, "
            f"x = {self.topology_calc.chi}"
        )
        self.renderer.add_text(text, position="top-left", key="topology")

    def run(self) -> None:
        """Запускает приложение: инициализация и основной цикл рендерера."""
        self.init()
        self.renderer.show()
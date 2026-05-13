from core.boundary_graph import BoundaryGraph
from core.drawable.disc import Disc
from core.factory import ObjectFactory
from core.drawable.plane import Plane
from core.geometry import angle_to_point, canon_arc
from core.ribbon_generator import RibbonGenerator
from gui.vedo_renderer import VedoRenderer
from core.topology import Topology
from core.constants import DISK_RADIUS
from core.interval_manager import RibbonManager
from gui.mouse_handler import MouseHandler
import time
import vedo

class Application:
    def __init__(self, renderer=None, topology_calculator=None, disc_radius=DISK_RADIUS):
        self.renderer = renderer or VedoRenderer()
        self.disc_radius = disc_radius
        self.disc = Disc(radius=disc_radius)
        self.plane = Plane(radius=disc_radius)
        self.factory = ObjectFactory()
        self.ribbon_gen = RibbonGenerator(disc_radius)
        self.ribbon_manager = RibbonManager()
        self.topology_calc = Topology(self.ribbon_manager.ribbons)

        self.mouse_handler = MouseHandler(
            get_ribbons_func=lambda: self.ribbon_manager.ribbons,
            disc_radius=disc_radius
        )
        self.mouse_handler.on_ribbon_updated = self._on_ribbon_changed

        self._adding_ribbon = False
        self._last_add_time = 0

        self.boundary_arcs = []

    def init(self):
        self.renderer.add_drawable(self.disc)
        self.renderer.add_drawable(self.plane)

        self.mouse_handler.attach(self.renderer)
        self.renderer.bind_key(self.on_key_press)
        self.renderer.add_text("Space - add a ribbon", position="bottom-left", key="hint")
        # self._update_topology_display()

    def on_key_press(self, evt):
        if evt.keypress == "space":
            self.add_random_ribbon()

    def add_random_ribbon(self, *args):
        # Проверка: если уже идёт добавление – выходим
        if self._adding_ribbon:
            return
        # Дополнительная защита от слишком частых кликов (0.5 сек)
        now = time.time()
        if now - self._last_add_time < 0.5:
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

    def _update_boundary(self):
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

        colors = ['purple', 'cyan', 'magenta', 'yellow']
        for i, cycle in enumerate(cycles):
            color = colors[i % len(colors)]
            for v1, v2, typ in cycle:
                arc = None
                if typ == 'disk':
                    p1 = angle_to_point(v1, DISK_RADIUS)
                    p2 = angle_to_point(v2, DISK_RADIUS)
                    raw = (v2 - v1) % 360
                    forward = (v1, v2) in disk_edges_set
                    if forward:
                        invert = raw > 180
                    else:
                        invert = raw < 180
                    arc = vedo.Arc(
                        center=(0, 0, 0),
                        point1=p1,
                        point2=p2,
                        invert=invert,
                        res=100
                    )
                elif typ == 'outer':
                    # start, end, _ = canon_arc(v1, v2)
                    # old_ribbon = graph.ribbon_outer[(start, end)]
                    # new_ribbon = old_ribbon
                    # new_ribbon.arcs[0].c(color)
                    # self.ribbon_manager.replace_ribbon(old_ribbon, new_ribbon)
                    start, end, _ = canon_arc(v1, v2)
                    old_ribbon = graph.ribbon_outer[(start, end)]
                    idx = self.ribbon_manager.ribbons.index(old_ribbon)
                    self.ribbon_manager.ribbons[idx].arcs[0].c(color)

                else:
                    start, end, _ = canon_arc(v1, v2)
                    old_ribbon = graph.ribbon_inner[(start, end)]
                    idx = self.ribbon_manager.ribbons.index(old_ribbon)
                    self.ribbon_manager.ribbons[idx].arcs[1].c(color)
                if not arc:
                    continue
                arc.c(color).lw(4)
                self.renderer.plotter.add(arc)
                self.boundary_arcs.append(arc)
        self.renderer.render()

    def _on_ribbon_changed(self, old_ribbon, new_ribbon):
        self.ribbon_manager.replace_ribbon(old_ribbon, new_ribbon)
        self._update_boundary()
        self._update_topology()

    def _update_topology(self):
        self.topology_calc.ribbons = self.ribbon_manager.ribbons
        self.topology_calc.compute()
        self.renderer.add_text(f"is_orientable={self.topology_calc.is_orientable}, "
                               f"g={self.topology_calc.g}, h={self.topology_calc.h}, m={self.topology_calc.m},"
                               f"x={self.topology_calc.chi}", position="top-left", key="topology")

    def run(self):
        self.init()
        self.renderer.show()
from core.disc import Disc
from core.factory import ObjectFactory
from core.ribbon_generator import RibbonGenerator
from gui.vedo_renderer import VedoRenderer
from core.topology import SimpleTopology
from core.constants import DISK_RADIUS
from core.interval_manager import RibbonManager
from gui.mouse_handler import MouseHandler
import time

class Application:
    def __init__(self, renderer=None, topology_calculator=None, disc_radius=DISK_RADIUS):
        self.renderer = renderer or VedoRenderer()
        self.topology_calc = topology_calculator or SimpleTopology()
        self.disc_radius = disc_radius
        self.disc = Disc(radius=disc_radius)
        self.factory = ObjectFactory()
        self.ribbon_gen = RibbonGenerator(disc_radius)
        self.ribbon_manager = RibbonManager()

        self.mouse_handler = MouseHandler(
            get_ribbons_func=lambda: self.ribbon_manager.ribbons,
            disc_radius=disc_radius
        )
        self.mouse_handler.on_ribbon_updated = self._on_ribbon_changed

        self._adding_ribbon = False
        self._last_add_time = 0

    def init(self):
        self.renderer.add_drawable(self.disc)

        self.renderer.add_button(self.add_random_ribbon, "Add a ribbon", position=(0.5, 0.05))
        self.mouse_handler.attach(self.renderer)
        # self._update_topology_display()

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
                self._update_topology()
        except Exception as e:
            print(f"Ошибка при добавлении ленточки: {e}")
        finally:
            self._adding_ribbon = False

    def _on_ribbon_changed(self, old_ribbon, new_ribbon):
        self.ribbon_manager.replace_ribbon(old_ribbon, new_ribbon)
        self._update_topology()

    def _update_topology(self):
        g, h, m = self.topology_calc.compute(self.ribbon_manager.ribbons)
        self.renderer.add_text(f"g={g}, h={h}, m={m}", position="top-left")

    def run(self):
        self.init()
        self.renderer.show()
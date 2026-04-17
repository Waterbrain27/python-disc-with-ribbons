from core.disc import Disc
from core.factory import ObjectFactory
from core.ribbon_generator import RibbonGenerator
from gui.vedo_renderer import VedoRenderer
from core.topology import SimpleTopology
from core.constants import DISK_RADIUS
from core.interval_manager import IntervalManager

class Application:
    def __init__(self, renderer=None, topology_calculator=None, disc_radius=DISK_RADIUS):
        self.renderer = renderer or VedoRenderer()
        self.topology_calc = topology_calculator or SimpleTopology()
        self.disc_radius = disc_radius
        self.disc = Disc(radius=disc_radius)
        self.factory = ObjectFactory()
        self.ribbon_gen = RibbonGenerator(disc_radius)
        self.interval_manager = IntervalManager()

    def init(self):
        self.renderer.add_drawable(self.disc)
        # Демо-ленточка
        ribbon = self.factory.create_ribbon(20, 170, 10, twist=0, radius=self.disc_radius, thickness=0)
        self.renderer.add_drawable(ribbon)

        self.renderer.add_button(self.add_random_ribbon, "Добавить ленточку", position=(0.5, 0.05))
        # self._update_topology_display()

    def add_random_ribbon(self, *args):
        new_ribbon = self.ribbon_gen.generate_random_ribbon(self.interval_manager)
        if new_ribbon:
            self.renderer.add_drawable(new_ribbon)
            self.interval_manager.update_from_ribbons(new_ribbon)
            # self._update_topology_display()

    # def _update_topology_display(self):
    #     # g, h, m = self.topology_calc.compute(self.ribbons)
    #     # self.renderer.add_text(f"g={g}, h={h}, m={m}", position="top-left")

    def run(self):
        self.init()
        self.renderer.show()
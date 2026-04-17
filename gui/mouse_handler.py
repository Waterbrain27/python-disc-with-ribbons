from core.interfaces import IInteractive
from core.geometry import point_to_angle

class MouseHandler(IInteractive):
    def __init__(self, get_ribbons_func, disc_radius=3.0, disc_center=(0,0,0)):
        self.get_ribbons = get_ribbons_func
        self.radius = disc_radius
        self.center = disc_center
        self.dragged_ribbon = None
        self.dragged_end = None
        self._renderer = None

    def attach(self, renderer):
        self._renderer = renderer
        renderer.bind_click(self.on_click)
        renderer.bind_move(self.on_drag)
        renderer.bind_release(self.on_release)

    def on_click(self, evt):
        if not hasattr(evt, 'actor') or evt.actor is None:
            return
        ribbons = self.get_ribbons()
        for ribbon in ribbons:
            for idx, pt in enumerate(ribbon.get_points()):
                if evt.actor == pt:
                    self.dragged_ribbon = ribbon
                    self.dragged_end = idx
                    return

    def on_drag(self, evt):
        if self.dragged_ribbon is None:
            return
        if not hasattr(evt, 'picked3d') or evt.picked3d is None:
            return
        pos3d = evt.picked3d
        angle = point_to_angle(pos3d, self.center)
        success = self.dragged_ribbon.update_angle(self.dragged_end, angle)
        if success:
            # Заменяем объект в рендерере (старый удаляем, новый добавляем)
            self._renderer.remove_drawable(self.dragged_ribbon)
            self._renderer.add_drawable(self.dragged_ribbon)
            self._renderer.render()

    def on_release(self, evt):
        self.dragged_ribbon = None
        self.dragged_end = None
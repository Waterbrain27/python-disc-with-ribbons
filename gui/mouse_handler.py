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
        self.on_ribbon_updated = None
        self._original_ribbon = None

    def attach(self, renderer):
        self._renderer = renderer
        renderer.bind_click(self.on_click)
        renderer.bind_move(self.on_drag)
        renderer.bind_right_click(self.on_right_click)

    def on_click(self, evt):
        # Если уже тянем и кликнули мимо точек — завершаем перетаскивание
        if self.dragged_ribbon is not None:
            ribbons = self.get_ribbons()
            hit = False
            if hasattr(evt, 'actor') and evt.actor is not None:
                for ribbon in ribbons:
                    for pt in ribbon.get_points():
                        if evt.actor == pt:
                            hit = True
                            break
            if not hit:
                self._finish_drag()
                return

        # Захват новой точки
        if not hasattr(evt, 'actor') or evt.actor is None:
            return
        ribbons = self.get_ribbons()
        for ribbon in ribbons:
            for idx, pt in enumerate(ribbon.get_points()):
                if evt.actor == pt:
                    self.dragged_ribbon = ribbon
                    self.dragged_end = idx
                    self._original_ribbon = ribbon
                    return

    def on_drag(self, evt):
        if self.dragged_ribbon is None:
            return
        if not hasattr(evt, 'picked3d') or evt.picked3d is None:
            return
        new_angle = point_to_angle(evt.picked3d, self.center)

        # Определяем новые углы
        if self.dragged_end == 0:
            new_a1, new_a2 = new_angle, self.dragged_ribbon.end_angle
        else:
            new_a1, new_a2 = self.dragged_ribbon.start_angle, new_angle

        new_ribbon = self.dragged_ribbon.clone_with_angles(new_a1, new_a2)
        if new_ribbon is None:
            return

        # Удаляем старый объект из сцены
        self._renderer.remove_drawable(self._original_ribbon)
        # Добавляем новый
        self._renderer.add_drawable(new_ribbon)

        # Сообщаем приложению о замене
        if self.on_ribbon_updated:
            self.on_ribbon_updated(self._original_ribbon, new_ribbon)

        # Теперь текущая перетаскиваемая ленточка — новая
        self.dragged_ribbon = new_ribbon
        self._original_ribbon = new_ribbon

    def on_right_click(self, evt):
        self._finish_drag()

    def _finish_drag(self):
        self.dragged_ribbon = None
        self.dragged_end = None
        self._original_ribbon = None

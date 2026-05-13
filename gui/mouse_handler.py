from typing import Callable, List, Optional, Tuple

from core.constants import DISK_RADIUS, DISK_CENTER
from core.managers.interfaces import IInteractive, IRenderer
from core.math_machinery.geometry import point_to_angle, bool_canon


class MouseHandler(IInteractive):
    """Обработчик взаимодействия мыши с ленточками (перетаскивание концов, правый клик)."""

    def __init__(
        self,
        get_ribbons_func: Callable[[], List['Ribbon']],
        disc_radius: float = DISK_RADIUS,
        disc_center: Tuple[float, float, float] = DISK_CENTER
    ) -> None:
        self.get_ribbons = get_ribbons_func
        self.is_interval_free = None
        self.radius = disc_radius
        self.center = disc_center
        self._renderer: Optional[IRenderer] = None
        self.on_ribbon_updated: Optional[Callable[['Ribbon', 'Ribbon'], None]] = None

        self.dragged_ribbon: Optional['Ribbon'] = None
        self.dragged_end: Optional[int] = None
        self._original_ribbon: Optional['Ribbon'] = None

    def attach(self, renderer: IRenderer) -> None:
        """Прикрепить обработчики событий к рендереру."""
        self._renderer = renderer
        renderer.bind_click(self.on_click)
        renderer.bind_move(self.on_mouse_move)
        renderer.bind_right_click(self.on_right_click)

    def on_click(self, evt: object) -> None:
        """Левый клик: начать перетаскивание конца ленточки."""
        if self.dragged_end is not None or self.dragged_ribbon is not None:
            self._finish_drag()
            return
        actor = getattr(evt, 'actor', None)
        if actor is None:
            return

        for ribbon in self.get_ribbons():
            for idx, pt in enumerate(ribbon.get_points()):
                if pt == actor:
                    self.dragged_ribbon = ribbon
                    self.dragged_end = idx
                    self._original_ribbon = ribbon
                    return

    def on_mouse_move(self, evt: object) -> None:
        """Движение мыши: обновлять положение перетаскиваемого конца."""
        if self.dragged_ribbon is None:
            return
        if not hasattr(evt, 'picked3d') or evt.picked3d is None:
            return
        new_angle = point_to_angle(evt.picked3d, self.center)
        if self.dragged_end == 0:
            new_a1, new_a2 = new_angle, self.dragged_ribbon.end_angle
        else:
            new_a1, new_a2 = self.dragged_ribbon.start_angle, new_angle

        if not bool_canon(new_a1, new_a2):
            new_a1, new_a2 = new_a2, new_a1
            self.dragged_end = 1 - self.dragged_end

        if not self.is_interval_free(new_a1, new_a2, self._original_ribbon):
            return

        new_ribbon = self.dragged_ribbon.clone_with_angles(new_a1, new_a2, self.dragged_ribbon.twist)
        if new_ribbon is None:
            return

        if self.on_ribbon_updated:
            self.on_ribbon_updated(self._original_ribbon, new_ribbon)

        self._renderer.remove_drawable(self._original_ribbon)
        self._renderer.add_drawable(new_ribbon)

        self.dragged_ribbon = new_ribbon
        self._original_ribbon = new_ribbon

    def on_right_click(self, evt: object) -> None:
        """Правый клик: переключить перекручивание ленточки."""
        actor = getattr(evt, 'actor', None)
        ribbons = self.get_ribbons()
        for ribbon in ribbons:
            if ribbon.get_mesh() == actor:
                new_ribbon = ribbon.clone_with_angles(ribbon.start_angle, ribbon.end_angle, 1 - ribbon.twist)
                self._renderer.remove_drawable(ribbon)
                self._renderer.add_drawable(new_ribbon)
                if self.on_ribbon_updated:
                    self.on_ribbon_updated(ribbon, new_ribbon)
                return

    def _finish_drag(self) -> None:
        """Завершить перетаскивание."""
        self.dragged_ribbon = None
        self.dragged_end = None
        self._original_ribbon = None
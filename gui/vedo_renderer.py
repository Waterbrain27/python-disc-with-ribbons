import vedo
import threading

from core.constants import WINDOW_SIZE, WINDOW_TITLE, BASIC_TEXT_COLOR, TEXT_SIZE
from core.managers.interfaces import IRenderer


class VedoRenderer(IRenderer):
    """Рендерер на основе vedo."""

    def __init__(self, title: str = WINDOW_TITLE, size: tuple = WINDOW_SIZE) -> None:
        self.plotter = vedo.Plotter(title=title, size=size)
        self._drawables = []
        self._text_actors = {}

    def add_drawable(self, obj: 'IDrawable') -> None:
        if obj:
            mesh = obj.get_mesh()
            if mesh is not None:
                self.plotter.add(mesh)
            if hasattr(obj, 'get_points'):
                for pt in obj.get_points():
                    self.plotter.add(pt)
            if hasattr(obj, 'get_arcs'):
                for arc in obj.get_arcs():
                    self.plotter.add(arc)

    def remove_drawable(self, obj: 'IDrawable') -> None:
        if obj:
            mesh = obj.get_mesh()
            if mesh is not None:
                self.plotter.remove(mesh)
            if hasattr(obj, 'get_points'):
                for pt in obj.get_points():
                    self.plotter.remove(pt)
            if hasattr(obj, 'get_arcs'):
                for arc in obj.get_arcs():
                    self.plotter.remove(arc)

    def render(self) -> None:
        self.plotter.render()

    def show(self) -> None:
        self.plotter.show(axes=1, viewup='z', interactive=True)

    def bind_key(self, callback) -> None:
        self.plotter.add_callback("key press", callback)

    def bind_click(self, callback) -> None:
        self.plotter.add_callback("mouse click", callback)

    def bind_right_click(self, callback) -> None:
        self.plotter.add_callback("mouse right click", callback)

    def bind_move(self, callback) -> None:
        self.plotter.add_callback("mouse move", callback)

    def bind_release(self, callback) -> None:
        self.plotter.add_callback("mouse button release", callback)

    def add_text(
        self,
        text: str,
        position: str | tuple = "top-left",
        key: str = "default",
        size: float = TEXT_SIZE,
        color: str = BASIC_TEXT_COLOR
    ) -> None:
        if key in self._text_actors:
            self.plotter.remove(self._text_actors[key])
        actor = vedo.Text2D(text, pos=position, font="Courier", s=size)
        actor.c(color)
        self.plotter.add(actor)
        self._text_actors[key] = actor

    def remove_text(self, key: str) -> None:
        """Удалить текст по ключу."""
        if key in self._text_actors:
            self.plotter.remove(self._text_actors[key])
            del self._text_actors[key]
import vedo

from core.constants import WINDOW_SIZE, WINDOW_TITLE
from core.interfaces import IRenderer


class VedoRenderer(IRenderer):
    """Рендерер на основе vedo."""

    def __init__(self, title: str = WINDOW_TITLE, size: tuple = WINDOW_SIZE) -> None:
        self.plotter = vedo.Plotter(title=title, size=size)
        self._drawables = []      # список добавленных IDrawable
        self._text_actors = {}   # для текста топологии

    def add_drawable(self, obj: 'IDrawable') -> None:
        mesh = obj.get_mesh()
        if mesh is not None:
            self.plotter.add(mesh)
        if hasattr(obj, 'get_points'):
            for pt in obj.get_points():
                self.plotter.add(pt)
        if hasattr(obj, 'get_arcs'):
            for arc in obj.get_arcs():
                self.plotter.add(arc)
        self.plotter.render()

    def remove_drawable(self, obj: 'IDrawable') -> None:
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

    def add_button(self, func, text: str, pos: tuple, c: str, bc: str, size: int):
        button = self.plotter.add_button(
            func,
            states=[text],
            pos=pos,
            c=c,
            bc=bc,
            size=size
        )
        return button

    def add_text(self, text: str, position: str = "top-left", key: str = "default") -> None:
        if key in self._text_actors:
            self.plotter.remove(self._text_actors[key])
        actor = vedo.Text2D(text, pos=position, font="Courier", s=1.2)
        self.plotter.add(actor)
        self._text_actors[key] = actor
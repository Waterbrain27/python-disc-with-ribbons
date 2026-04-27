import vedo
from core.interfaces import IRenderer

class VedoRenderer(IRenderer):
    def __init__(self, title="Disc with ribbons", size=(800, 500)):
        self.plotter = vedo.Plotter(title=title, size=size)
        self._drawables = []      # список добавленных IDrawable
        self._text_actor = None   # для текста топологии

    def add_drawable(self, obj):
        mesh = obj.get_mesh()
        if mesh is not None:
            self.plotter.add(mesh)
            print("Меш добавлен")  # временная отладка
        if hasattr(obj, 'get_points'):
            for pt in obj.get_points():
                self.plotter.add(pt)
                print(f"Добавлена точка: {pt}")  # отладка
        self.plotter.render()

    def remove_drawable(self, obj):
        mesh = obj.get_mesh()
        if mesh is not None:
            self.plotter.remove(mesh)
        if hasattr(obj, 'get_points'):
            for pt in obj.get_points():
                self.plotter.remove(pt)
        self.plotter.render()

    def render(self):
        self.plotter.render()

    def show(self):
        self.plotter.show(axes=1, viewup='z', interactive=True)

    def add_button(self, callback, text: str, position=(0.5, 0.05)):
        self.plotter.add_button(
            callback,
            pos=position,
            states=[text],
            c="orange",
            bc="green",
            font="Arial",
            size=16
        )

    def bind_click(self, callback):
        self.plotter.add_callback("mouse click", callback)

    def bind_right_click(self, callback):
        self.plotter.add_callback("mouse right click", callback)

    def bind_move(self, callback):
        self.plotter.add_callback("mouse move", callback)

    def bind_release(self, callback):
        self.plotter.add_callback("mouse button release", callback)

    def add_text(self, text: str, position: str = "top-left"):
        if self._text_actor is not None:
            self.plotter.remove(self._text_actor)
        self._text_actor = vedo.Text2D(text, pos=position, font="Courier", s=1.2)
        self.plotter.add(self._text_actor)
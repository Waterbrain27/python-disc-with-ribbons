import vedo
from core.interfaces import IRenderer

class VedoRenderer(IRenderer):
    def __init__(self, title="Disc with ribbons", size=(800, 500)):
        self.plotter = vedo.Plotter(title=title, size=size)
        self._drawables = []      # список добавленных IDrawable
        self._text_actor = None   # для текста топологии

    def add_drawable(self, obj):
        print(f"Добавляем объект: {obj}")  # <-- добавить
        mesh = obj.get_mesh()
        if mesh is None:
            print("ОШИБКА: get_mesh() вернул None!")  # <-- добавить
            return
        print(f"Меш получен: {mesh}, добавляем в plotter...")  # <-- добавить
        self.plotter.add(mesh)
        self.plotter.render()  # <-- убедитесь, что эта строка есть
        print("Рендер вызван.")  # <-- добавить

    def remove_drawable(self, obj):
        if obj in self._drawables:
            self._drawables.remove(obj)
        mesh = obj.get_mesh()
        if mesh is not None:
            self.plotter.remove(mesh)
        if hasattr(obj, 'get_points'):
            for pt in obj.get_points():
                self.plotter.remove(pt)

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

    def bind_move(self, callback):
        self.plotter.add_callback("mouse move", callback)

    def bind_release(self, callback):
        self.plotter.add_callback("mouse button release", callback)

    def add_text(self, text: str, position: str = "top-left"):
        if self._text_actor is not None:
            self.plotter.remove(self._text_actor)
        self._text_actor = vedo.Text2D(text, pos=position, font="Courier", s=1.2)
        self.plotter.add(self._text_actor)
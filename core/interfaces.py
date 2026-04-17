from abc import ABC, abstractmethod
from typing import List, Tuple, Any, Optional

class IDrawable(ABC):
    """Объект, который можно отрисовать."""
    @abstractmethod
    def get_mesh(self):
        """Вернуть 3D меш (объект, специфичный для рендерера)."""
        pass

class IRenderer(ABC):
    """Абстрактный графический движок."""
    @abstractmethod
    def add_drawable(self, obj: IDrawable) -> None:
        """Добавить объект на сцену."""
        pass

    @abstractmethod
    def remove_drawable(self, obj: IDrawable) -> None:
        """Удалить объект со сцены."""
        pass

    @abstractmethod
    def render(self) -> None:
        """Принудительно перерисовать сцену."""
        pass

    @abstractmethod
    def show(self) -> None:
        """Запустить главный цикл отображения."""
        pass

    @abstractmethod
    def add_button(self, callback, text: str, position: tuple = (0.5, 0.05)) -> None:
        """Добавить кнопку."""
        pass

    @abstractmethod
    def bind_click(self, callback) -> None:
        """Привязать обработчик клика мыши."""
        pass

    @abstractmethod
    def add_text(self, text: str, position: str = "top-left") -> None:
        """Показать текст в углу."""
        pass

    @abstractmethod
    def bind_move(self, callback):
        pass

    @abstractmethod
    def bind_release(self, callback):
        pass

class ITopologyCalculator(ABC):
    """Стратегия вычисления топологического типа."""
    @abstractmethod
    def compute(self, ribbons: List['Ribbon']) -> Tuple[int, int, int]:
        """Вернуть (g, h, m)."""
        pass

class IInteractive(ABC):
    """Обработчик ввода (мышь, клавиатура)."""
    @abstractmethod
    def attach(self, renderer: IRenderer) -> None:
        """Привязать обработчики к рендереру."""
        pass
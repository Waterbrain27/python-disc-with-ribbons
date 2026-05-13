from abc import ABC, abstractmethod
from typing import List, Tuple, Any, Optional

class IDrawable(ABC):
    """Интерфейс объекта, который можно отрисовать в сцене"""
    @abstractmethod
    def get_mesh(self) -> Any:
        """Возвращает mesh-объект"""
        pass

class IRenderer(ABC):
    """Абстрактный интерфейс рендерера сцены"""
    @abstractmethod
    def add_drawable(self, obj: IDrawable) -> None:
        """Добавить объект на сцену"""
        pass

    @abstractmethod
    def remove_drawable(self, obj: IDrawable) -> None:
        """Удалить объект со сцены"""
        pass

    @abstractmethod
    def render(self) -> None:
        """Принудительно перерисовать сцену"""
        pass

    @abstractmethod
    def show(self) -> None:
        """Запустить интерактивный цикл рендерера"""
        pass

    @abstractmethod
    def bind_key(self, callback) -> None:
        """Назначить обработчик нажатия клавиш"""
        pass

    @abstractmethod
    def bind_click(self, callback) -> None:
        """Назначить обработчик клика левой кнопкой мыши"""
        pass

    @abstractmethod
    def add_text(self, text: str, position: str = "top-left") -> None:
        """Добавить текстовый блок на сцену (перезаписывает предыдущий)"""
        pass

    @abstractmethod
    def bind_move(self, callback) -> None:
        """Назначить обработчик движения мыши"""
        pass

    @abstractmethod
    def bind_right_click(self, callback) -> None:
        """Назначить обработчик клика правой кнопкой мыши"""
        pass

    @abstractmethod
    def bind_release(self, callback) -> None:
        """Назначить обработчик отпускания кнопки мыши"""
        pass

class ITopologyCalculator(ABC):
    """Интерфейс для вычисления топологических инвариантов поверхности"""
    @abstractmethod
    def compute(self) -> None:
        """Вычислить g, h, m, χ, ориентируемость"""
        pass

class IInteractive(ABC):
    """Интерфейс для объекта, который может взаимодействовать с рендерером"""
    @abstractmethod
    def attach(self, renderer: IRenderer) -> None:
        """Прикрепить обработчики событий к рендереру"""
        pass
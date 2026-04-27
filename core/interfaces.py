from abc import ABC, abstractmethod
from typing import List, Tuple, Any, Optional

class IDrawable(ABC):
    @abstractmethod
    def get_mesh(self):
        pass

class IRenderer(ABC):
    @abstractmethod
    def add_drawable(self, obj: IDrawable) -> None:
        pass

    @abstractmethod
    def remove_drawable(self, obj: IDrawable) -> None:
        pass

    @abstractmethod
    def render(self) -> None:
        pass

    @abstractmethod
    def show(self) -> None:
        pass

    @abstractmethod
    def add_button(self, callback, text: str, position: tuple = (0.5, 0.05)) -> None:
        pass

    @abstractmethod
    def bind_click(self, callback) -> None:
        pass

    @abstractmethod
    def add_text(self, text: str, position: str = "top-left") -> None:
        pass

    @abstractmethod
    def bind_move(self, callback):
        pass

    @abstractmethod
    def bind_right_click(self, callback):
        pass

    @abstractmethod
    def bind_release(self, callback):
        pass

class ITopologyCalculator(ABC):
    @abstractmethod
    def compute(self, ribbons: List['Ribbon']) -> Tuple[int, int, int]:
        pass

class IInteractive(ABC):
    @abstractmethod
    def attach(self, renderer: IRenderer) -> None:
        pass
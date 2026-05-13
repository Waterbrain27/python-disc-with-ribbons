from core.constants import DISK_RADIUS, RIBBON_RADIUS, RIBBON_DEFAULT_TWIST, RIBBON_DEFAULT_THICKNESS
from core.drawable.ribbon import Ribbon
from core.topology import Topology, ITopologyCalculator


class ObjectFactory:
    """Фабрика для создания ленточек и вычислителей топологии."""

    @staticmethod
    def create_ribbon(
        angle1: float,
        angle2: float,
        width: float,
        twist: int = RIBBON_DEFAULT_TWIST,
        radius: float = RIBBON_RADIUS,
        thickness: float = RIBBON_DEFAULT_THICKNESS,
        random_height: bool = True,
        height: float = 0.0
    ) -> Ribbon:
        """
        Создать экземпляр Ribbon.

        Args:
            angle1: начальный угол в градусах.
            angle2: конечный угол в градусах.
            width: ширина ленточки (угловое смещение) в градусах.
            twist: 0 — без перекручивания, 1 — с перекручиванием (лента Мёбиуса).
            radius: радиус диска.
            thickness: толщина 3D-выдавливания.
            random_height: выбирать ли высоту случайно.
            height: высота ленточки (если не случайная).
        """
        return Ribbon(angle1, angle2, width, twist, radius, thickness, random_height, height)

    @staticmethod
    def create_topology_calculator(mode: str = 'simple') -> ITopologyCalculator:
        """
        Создать вычислитель топологии.

        Args:
            mode: 'simple' для базовой топологии.

        Returns:
            Экземпляр ITopologyCalculator.
        """
        if mode == 'simple':
            return Topology()
        else:
            raise ValueError(f"Неизвестный режим топологии: {mode}")
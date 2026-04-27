from core.ribbon import Ribbon
from core.topology import SimpleTopology, ITopologyCalculator

class ObjectFactory:
    @staticmethod
    def create_ribbon(angle1: float, angle2: float, width: float,
                      twist: int = 0, radius: float = 3.0, thickness: float = 0.0,
                      random_height: bool = True, height: float = 0.0) -> Ribbon:
        return Ribbon(angle1, angle2, width, twist, radius, thickness, random_height, height)

    @staticmethod
    def create_topology_calculator(mode: str = 'simple') -> ITopologyCalculator:
        if mode == 'simple':
            return SimpleTopology()
        else:
            raise ValueError(f"Unknown topology mode: {mode}")
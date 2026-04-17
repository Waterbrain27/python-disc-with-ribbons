from typing import List, Tuple
from core.interfaces import ITopologyCalculator
from core.ribbon import Ribbon

class SimpleTopology(ITopologyCalculator):
    def compute(self, ribbons: List[Ribbon]) -> Tuple[int, int, int]:
        g = sum(1 for r in ribbons if r.twist == 0)
        m = sum(1 for r in ribbons if r.twist == 1)
        return g, 0, m   # h = 0 пока
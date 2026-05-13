from typing import List, Tuple, Dict, Set, Optional
from core.math_machinery.geometry import canon_arc, angle_in_interval_strictly


class BoundaryGraph:
    """Граф, представляющий границу диска после приклеивания ленточек."""

    def __init__(self, ribbons: List['Ribbon']) -> None:
        """
        Args:
            ribbons: список объектов Ribbon, прикреплённых к диску.
        """
        self.ribbons = ribbons
        self.vertices: List[float] = []          # отсортированные углы (градусы)
        self.disk_edges: List[Tuple[float, float]] = []   # свободные интервалы на диске
        self.ribbon_outer: Dict[Tuple[float, float], 'Ribbon'] = {}   # внешние рёбра ленточек
        self.ribbon_inner: Dict[Tuple[float, float], 'Ribbon'] = {}   # внутренние рёбра ленточек

    def build(self) -> None:
        """Построить вершины, рёбра диска и отображение рёбер ленточек."""
        self.vertices.clear()
        self.disk_edges.clear()
        self.ribbon_outer.clear()
        self.ribbon_inner.clear()

        # Собрать все занятые интервалы и запомнить их концы
        occupied: List[List[float]] = []
        for r in self.ribbons:
            start, end, _ = canon_arc(r.start_angle, r.end_angle)
            w = r.width
            # два приклеенных интервала одной ленточки
            int1 = [start, (start + w) % 360]
            int2 = [(end - w) % 360, end]
            occupied.append(int1)
            occupied.append(int2)
            # вершины – концы этих интервалов
            self.vertices.extend([int1[0], int1[1], int2[0], int2[1]])

        # Уникальные вершины и сортировка
        self.vertices = sorted(set(v % 360 for v in self.vertices))

        # Свободные интервалы: между соседними вершинами, если не покрыты занятыми
        n = len(self.vertices)
        for i in range(n):
            v1 = self.vertices[i]
            v2 = self.vertices[(i + 1) % n]
            mid = (v1 + ((v2 - v1) % 360) / 2) % 360
            covered = any(angle_in_interval_strictly(mid, (a, b)) for a, b in occupied)
            if not covered:
                self.disk_edges.append((v1, v2))

        # Рёбра ленточек
        for r in self.ribbons:
            start, end, _ = canon_arc(r.start_angle, r.end_angle)
            w = r.width
            inner_start = (start + w) % 360
            inner_end = (end - w) % 360
            if r.twist == 0:
                outer_pair = (start, end)
                inner_pair = (inner_start, inner_end)
            else:
                outer_pair = (inner_start, end)
                inner_pair = (start, inner_end)
            self.ribbon_outer[outer_pair] = r
            self.ribbon_inner[inner_pair] = r

    def get_cycles(self) -> List[List[Tuple[float, float, str]]]:
        """
        Возвращает список циклов, обходя вершины по кратчайшему направлению.

        Каждый цикл — это список кортежей (вершина1, вершина2, тип_ребра).
        Типы рёбер: 'disk', 'outer', 'inner'.
        """
        adj: Dict[float, List[Tuple[float, str]]] = {v: [] for v in self.vertices}
        for v1, v2 in self.disk_edges:
            adj[v1].append((v2, 'disk'))
            adj[v2].append((v1, 'disk'))
        for (v1, v2) in self.ribbon_outer:
            adj[v1].append((v2, 'outer'))
            adj[v2].append((v1, 'outer'))
        for (v1, v2) in self.ribbon_inner:
            adj[v1].append((v2, 'inner'))
            adj[v2].append((v1, 'inner'))

        visited: Set[float] = set()
        cycles: List[List[Tuple[float, float, str]]] = []

        for start in self.vertices:
            if start in visited:
                continue
            cycle: List[Tuple[float, float, str]] = []
            current = start
            prev: Optional[float] = None
            prev_type: Optional[str] = None
            while True:
                visited.add(current)
                candidates = [(n, t) for (n, t) in adj[current] if (n, t) != (prev, prev_type)]
                next_v, edge_type = candidates[0]
                cycle.append((current, next_v, edge_type))
                prev, prev_type, current = current, edge_type, next_v
                if current == start:
                    break
            cycles.append(cycle)
        return cycles
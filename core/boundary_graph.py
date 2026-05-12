from core.geometry import canon_arc, angle_in_interval, angle_in_interval_strictly


class BoundaryGraph:
    def __init__(self, ribbons):
        self.ribbons = ribbons
        self.vertices = []        # отсортированные углы (float)
        self.disk_edges = []      # [(v1, v2)]
        self.ribbon_outer = {}    # {(v1, v2): ribbon}
        self.ribbon_inner = {}    # {(v1, v2): ribbon}

    def build(self):
        self.vertices.clear()
        self.disk_edges.clear()
        self.ribbon_outer.clear()
        self.ribbon_inner.clear()

        # Собираем все занятые интервалы и запоминаем точки – концы интервалов
        occupied = []  # [(start, end), ...]
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

        # Уникальные вершины, сортировка
        self.vertices = sorted(set(v % 360 for v in self.vertices))

        # Свободные интервалы: между соседними вершинами, если не покрыт занятым
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
        # print(self.ribbon_inner, " <- inner pairs")
        # print(self.ribbon_outer, " <- outer pairs")
        # print(self.disk_edges, " <- free intervals (disk edges)")

    def get_cycles(self):
        """Возвращает список циклов, обходя вершины по кратчайшему направлению."""
        adj = {v: [] for v in self.vertices}
        for v1, v2 in self.disk_edges:
            adj[v1].append((v2, 'disk'))
            adj[v2].append((v1, 'disk'))
        for (v1, v2) in self.ribbon_outer:
            adj[v1].append((v2, 'outer'))
            adj[v2].append((v1, 'outer'))
        for (v1, v2) in self.ribbon_inner:
            adj[v1].append((v2, 'inner'))
            adj[v2].append((v1, 'inner'))
        visited = set()
        cycles = []
        # print(f"vertices before calculating cycles: {self.vertices}")
        for start in self.vertices:
            if start in visited:
                continue
            cycle = []
            current = start
            prev = None
            prev_type = None
            while True:
                visited.add(current)
                # print(f"current: {current}\nprev: {prev}\nprev type: {prev_type}")
                candidates = [(n, t) for (n, t) in adj[current] if (n, t) != (prev, prev_type)]
                # print(f"adjusts of current: {adj[current]}")
                # print(f"{candidates} <- candidates with current {current}\n")
                # if len(candidates) == 2:
                #     pass
                next_v, edge_type = candidates[0]
                cycle.append((current, next_v, edge_type))
                prev, prev_type, current = current, edge_type, next_v
                # print(f"picked vertice {current} with type {edge_type}")
                if current == start:
                    break
            cycles.append(cycle)
            # print(f"result cycle: {cycle}\n")
        return cycles
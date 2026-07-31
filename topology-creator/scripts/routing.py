#!/usr/bin/env python3
"""Obstacle-avoiding orthogonal routing for topology links.

draw.io's own router only knows about the two endpoints, so on a dense diagram
it happily draws a trunk straight through three server icons and a row of
captions. This module plans each path on a coarse grid that knows where every
icon, caption and zone header actually sits, and hands draw.io explicit
waypoints instead.

Search is A* over (x, y, direction) with three costs:

  - distance, so paths stay short
  - a turn penalty, so paths stay straight instead of stair-stepping
  - a reuse penalty, so links that share a corridor run side by side rather
    than printing on top of each other

Stdlib only, like the rest of the skill.
"""

import heapq

GRID = 10               # planning resolution in px; finer is slower, not better
TURN_COST = 14          # discourage staircases
REUSE_COST = 9          # nudge parallel links into their own lane
CLEARANCE = 8           # keep this far off icons and text
ZONE_CROSS_COST = 7     # prefer the margins over cutting through a zone

# (dx, dy) per direction index
STEPS = ((1, 0), (-1, 0), (0, 1), (0, -1))


class Obstacles:
    """A blocked-cell map built from icon boxes, captions and zone headers.

    Captions are hard obstacles for *every* link, including the links attached
    to the device they belong to. Only an icon's own box may be entered by its
    own links -- otherwise a link leaving a node's bottom edge drives straight
    down through that node's own device name, which is the exact thing this
    module exists to prevent.
    """

    def __init__(self, width: float, height: float) -> None:
        self.w = int(width // GRID) + 4
        self.h = int(height // GRID) + 4
        self.blocked: set[tuple[int, int]] = set()
        self.owner: dict[tuple[int, int], str] = {}
        self.zones: dict[tuple[int, int], tuple] = {}

    def add_rect(self, x, y, w, h, owner: str | None = None,
                 clearance: float | None = None) -> None:
        for cell in self._cells(x, y, w, h, clearance):
            self.blocked.add(cell)
            if owner is not None:
                self.owner[cell] = owner
            else:
                # A hard obstacle with no owner can never be entered; make sure
                # an earlier owner claim does not keep it passable.
                self.owner.pop(cell, None)

    def add_zone(self, x, y, w, h, zone_id: str) -> None:
        """Zone interiors are passable but discouraged -- see ZONE_CROSS_COST."""
        for cell in self._cells(x, y, w, h, 0):
            self.zones[cell] = self.zones.get(cell, ()) + (zone_id,)

    def _cells(self, x, y, w, h, clearance: float | None = None):
        pad = CLEARANCE if clearance is None else clearance
        x0 = int((x - pad) // GRID)
        x1 = int((x + w + pad) // GRID)
        y0 = int((y - pad) // GRID)
        y1 = int((y + h + pad) // GRID)
        for gx in range(x0, x1 + 1):
            for gy in range(y0, y1 + 1):
                yield gx, gy

    def free(self, cell, allow: tuple) -> bool:
        gx, gy = cell
        if not (0 <= gx < self.w and 0 <= gy < self.h):
            return False
        if cell not in self.blocked:
            return True
        # A link may only enter its own endpoints' icon boxes.
        return self.owner.get(cell) in allow

    def zone_penalty(self, cell, allow_zones: frozenset) -> float:
        crossed = self.zones.get(cell)
        if not crossed:
            return 0.0
        return ZONE_CROSS_COST * sum(1 for z in crossed if z not in allow_zones)


def _to_grid(point) -> tuple[int, int]:
    return int(round(point[0] / GRID)), int(round(point[1] / GRID))


def _direction(from_cell, to_cell) -> int:
    dx = to_cell[0] - from_cell[0]
    dy = to_cell[1] - from_cell[1]
    for i, (sx, sy) in enumerate(STEPS):
        if (dx > 0) == (sx > 0) and (dx < 0) == (sx < 0) \
           and (dy > 0) == (sy > 0) and (dy < 0) == (sy < 0):
            return i
    return 0


def plan(start, end, obstacles: Obstacles, used: dict,
         allow: tuple, start_dir: int | None = None,
         end_dir: int | None = None,
         allow_zones: frozenset = frozenset()) -> list[tuple[float, float]]:
    """Route start -> end around obstacles. Returns [] if no path exists.

    `start` and `end` are absolute px points on the two icons' perimeters.
    `allow` names the two endpoint owners whose footprints may be entered.
    `used` counts how many prior paths crossed each cell.
    """
    s = _to_grid(start)
    e = _to_grid(end)
    if s == e:
        return []

    open_heap = [(0, s, -1 if start_dir is None else start_dir, None)]
    best: dict[tuple, float] = {}
    parents: dict[tuple, tuple] = {}

    def heuristic(cell) -> float:
        return (abs(cell[0] - e[0]) + abs(cell[1] - e[1])) * 1.0

    goal_state = None
    while open_heap:
        priority, cell, direction, parent = heapq.heappop(open_heap)
        state = (cell, direction)
        if state in best and best[state] <= priority - heuristic(cell):
            continue
        cost = priority - heuristic(cell)
        best[state] = cost
        parents[state] = parent

        if cell == e and (end_dir is None or direction == end_dir):
            goal_state = state
            break

        for i, (dx, dy) in enumerate(STEPS):
            nxt = (cell[0] + dx, cell[1] + dy)
            if not obstacles.free(nxt, allow):
                continue
            step = 1.0
            if direction != -1 and i != direction:
                step += TURN_COST
            step += REUSE_COST * used.get(nxt, 0)
            step += obstacles.zone_penalty(nxt, allow_zones)
            ncost = cost + step
            nstate = (nxt, i)
            if nstate in best and best[nstate] <= ncost:
                continue
            heapq.heappush(open_heap, (ncost + heuristic(nxt), nxt, i, state))

    if goal_state is None:
        return []

    # Walk parents back to the start.
    cells = []
    state = goal_state
    while state is not None:
        cells.append(state[0])
        state = parents.get(state)
    cells.reverse()

    for c in cells:
        used[c] = used.get(c, 0) + 1

    return _simplify([(c[0] * GRID, c[1] * GRID) for c in cells])


def _simplify(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Drop collinear midpoints; draw.io only needs the corners."""
    if len(points) < 3:
        return []
    out = [points[0]]
    for prev, cur, nxt in zip(points, points[1:], points[2:]):
        if (cur[0] - prev[0], cur[1] - prev[1]) != (nxt[0] - cur[0], nxt[1] - cur[1]):
            out.append(cur)
    out.append(points[-1])
    # The endpoints themselves are implied by the edge's source/target.
    return out[1:-1]

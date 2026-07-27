from __future__ import annotations

import heapq
from itertools import count
from typing import Callable

from .model import Checkpoint, Point


def manhattan(a: Point, b: Point) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def neighbors(node: Point, w: int, h: int, blocked: set[Point]) -> list[Point]:
    x, y = node
    out: list[Point] = []
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = x + dx, y + dy
        if 1 <= nx <= w and 1 <= ny <= h and (nx, ny) not in blocked:
            out.append((nx, ny))
    return out


def reconstruct(came_from: dict[Point, Point], current: Point) -> list[Point]:
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.insert(0, current)
    return path


def astar_simple(start: Point, goal: Point, w: int, h: int, blocked: set[Point]) -> list[Point] | None:
    open_list: list[Point] = [start]
    in_open = {start}

    came_from: dict[Point, Point] = {}
    g_score = {start: 0}
    f_score = {start: manhattan(start, goal)}

    while open_list:
        current = min(open_list, key=lambda n: f_score.get(n, 10**12))
        open_list.remove(current)
        in_open.discard(current)

        if current == goal:
            return reconstruct(came_from, current)

        for n in neighbors(current, w, h, blocked):
            tentative = g_score[current] + 1
            if tentative < g_score.get(n, 10**12):
                came_from[n] = current
                g_score[n] = tentative
                f_score[n] = tentative + manhattan(n, goal)
                if n not in in_open:
                    open_list.append(n)
                    in_open.add(n)

    return None


def astar_heap(start: Point, goal: Point, w: int, h: int, blocked: set[Point]) -> list[Point] | None:
    # Tie-breaker avoids comparing tuple nodes when f-score is equal.
    tiebreak = count()
    heap: list[tuple[int, int, Point]] = [(manhattan(start, goal), next(tiebreak), start)]

    came_from: dict[Point, Point] = {}
    g_score = {start: 0}
    closed: set[Point] = set()

    while heap:
        _, _, current = heapq.heappop(heap)
        if current in closed:
            continue
        closed.add(current)

        if current == goal:
            return reconstruct(came_from, current)

        for n in neighbors(current, w, h, blocked):
            tentative = g_score[current] + 1
            if tentative < g_score.get(n, 10**12):
                came_from[n] = current
                g_score[n] = tentative
                f = tentative + manhattan(n, goal)
                heapq.heappush(heap, (f, next(tiebreak), n))

    return None


def collect_unlocked_unreached(root: Checkpoint) -> list[Checkpoint]:
    out: list[Checkpoint] = []

    def walk(node: Checkpoint) -> None:
        if node.id != "root" and node.unlocked and not node.reached:
            out.append(node)
        for child in node.children:
            walk(child)

    walk(root)
    return out


def choose_next_shortest_path(
    player: Point,
    root: Checkpoint,
    w: int,
    h: int,
    blocked: set[Point],
    method: str = "heap",
) -> tuple[list[Point] | None, Checkpoint | None]:
    algo: Callable[[Point, Point, int, int, set[Point]], list[Point] | None]
    algo = astar_heap if method == "heap" else astar_simple

    best_path: list[Point] | None = None
    best_node: Checkpoint | None = None
    best_len = 10**12

    for node in collect_unlocked_unreached(root):
        path = algo(player, node.pos, w, h, blocked)
        if path is not None and len(path) < best_len:
            best_path = path
            best_node = node
            best_len = len(path)

    return best_path, best_node

from __future__ import annotations

from dataclasses import dataclass

from .model import Checkpoint, Point
from .pathfinding import choose_next_shortest_path


@dataclass
class GameState:
    grid_w: int
    grid_h: int
    blocked: set[Point]
    player: Point
    root: Checkpoint
    method: str = "heap"
    active_path: list[Point] | None = None
    active_target: Checkpoint | None = None
    path_index: int = 1

    def all_reached(self) -> bool:
        def walk(node: Checkpoint) -> bool:
            if node.id != "root" and not node.reached:
                return False
            return all(walk(c) for c in node.children)

        return walk(self.root)

    def unlock_children(self, node: Checkpoint) -> None:
        for child in node.children:
            child.unlocked = True

    def plan_if_needed(self) -> None:
        if self.active_path is None:
            self.active_path, self.active_target = choose_next_shortest_path(
                player=self.player,
                root=self.root,
                w=self.grid_w,
                h=self.grid_h,
                blocked=self.blocked,
                method=self.method,
            )
            self.path_index = 1

    def tick(self) -> str:
        self.plan_if_needed()

        if self.active_path is None:
            return "no-path"

        if self.path_index < len(self.active_path):
            self.player = self.active_path[self.path_index]
            self.path_index += 1

        if self.active_target and self.player == self.active_target.pos:
            reached_id = self.active_target.id
            self.active_target.reached = True
            self.unlock_children(self.active_target)
            self.active_path = None
            self.active_target = None
            return f"reached:{reached_id}"

        return f"move:{self.player[0]},{self.player[1]}"


def build_sample_tree() -> Checkpoint:
    c = Checkpoint(id="C", pos=(8, 3), unlocked=False)
    d = Checkpoint(id="D", pos=(8, 7), unlocked=False)
    a = Checkpoint(id="A", pos=(5, 2), unlocked=True, children=[c])
    b = Checkpoint(id="B", pos=(4, 6), unlocked=True, children=[d])
    root = Checkpoint(id="root", pos=(2, 2), reached=True, unlocked=True, children=[a, b])
    return root

from __future__ import annotations

from dataclasses import dataclass, field


Point = tuple[int, int]


@dataclass
class Checkpoint:
    id: str
    pos: Point
    reached: bool = False
    unlocked: bool = False
    children: list["Checkpoint"] = field(default_factory=list)

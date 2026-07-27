from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .bmp_loader import BitmapImage, load_1bit_bmp


@dataclass
class BitmapBackedCPU:
    width: int = 0
    height: int = 0
    memory: list[int] = field(default_factory=list)
    program_counter: int = 0

    def load_bitmap(self, path: str | Path) -> BitmapImage:
        image = load_1bit_bmp(path)
        self.width = image.width
        self.height = image.height
        self.memory = image.flatten_bits()
        self.program_counter = 0
        return image

    def reset(self) -> None:
        self.program_counter = 0

    def step(self) -> int:
        if not self.memory:
            raise RuntimeError("CPU memory is empty. Load a bitmap first.")
        if self.program_counter >= len(self.memory):
            raise StopIteration("Program counter moved beyond loaded bitmap memory.")

        bit = self.memory[self.program_counter]
        self.program_counter += 1
        return bit

    def dump_memory(self) -> str:
        if not self.memory:
            return ""

        rows = []
        for row_start in range(0, len(self.memory), self.width):
            row = self.memory[row_start : row_start + self.width]
            rows.append("".join(str(bit) for bit in row))
        return "\n".join(rows)

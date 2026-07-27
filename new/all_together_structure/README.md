# all-together-structure

Checkpoint tree progression + shortest path recalculation for games.

## Features

- Tree-based checkpoint unlock flow
- Recompute next shortest target after each checkpoint is reached
- Two A* strategies:
  - `simple`: list-based open set (easy to read)
  - `heap`: priority-queue open set (faster)
- CLI demo for quick checks

## Install

```bash
pip install -e .
```

## Run demo

```bash
ats-demo --method heap
ats-demo --method simple
```

## Use in code

```python
from all_together_structure.game import GameState, build_sample_tree

state = GameState(
    grid_w=10,
    grid_h=10,
    blocked={(6, 2), (6, 3), (6, 4)},
    player=(2, 2),
    root=build_sample_tree(),
    method="heap",
)

while not state.all_reached():
    status = state.tick()
    print(status)
```

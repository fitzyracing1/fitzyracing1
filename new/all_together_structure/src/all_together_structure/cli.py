from __future__ import annotations

import argparse

from .game import GameState, build_sample_tree


def main() -> None:
    parser = argparse.ArgumentParser(description="Run checkpoint-tree shortest-path demo")
    parser.add_argument("--method", choices=["simple", "heap"], default="heap")
    parser.add_argument("--steps", type=int, default=80)
    args = parser.parse_args()

    state = GameState(
        grid_w=10,
        grid_h=10,
        blocked={(6, 2), (6, 3), (6, 4)},
        player=(2, 2),
        root=build_sample_tree(),
        method=args.method,
    )

    print(f"method={args.method}")
    for _ in range(args.steps):
        status = state.tick()
        print(status)
        if state.all_reached():
            print("complete")
            break


if __name__ == "__main__":
    main()

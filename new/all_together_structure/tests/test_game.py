from all_together_structure.game import GameState, build_sample_tree


def run_to_finish(method: str) -> bool:
    state = GameState(
        grid_w=10,
        grid_h=10,
        blocked={(6, 2), (6, 3), (6, 4)},
        player=(2, 2),
        root=build_sample_tree(),
        method=method,
    )
    for _ in range(200):
        state.tick()
        if state.all_reached():
            return True
    return False


def test_heap_completes() -> None:
    assert run_to_finish("heap")


def test_simple_completes() -> None:
    assert run_to_finish("simple")

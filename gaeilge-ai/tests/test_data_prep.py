from gaeilge_ai.data_prep import Pair, dedupe, split, write_tsv, read_tsv


def test_dedupe_drops_dupes_and_empties():
    pairs = [
        Pair("Hello", "Dia duit"),
        Pair("hello", "Dia duit"),
        Pair("Hello", "Conas atá tú"),
        Pair("", "Foo"),
        Pair("World", ""),
        Pair("World", "Domhan"),
    ]
    out = dedupe(pairs)
    srcs = [p.src for p in out]
    assert srcs == ["Hello", "World"]


def test_split_sizes_sum_to_total():
    pairs = [Pair(f"src{i}", f"tgt{i}") for i in range(1000)]
    parts = split(pairs, dev_frac=0.1, test_frac=0.1, seed=1)
    assert len(parts["test"]) == 100
    assert len(parts["dev"]) == 100
    assert len(parts["train"]) == 800
    seen = {p.src for part in parts.values() for p in part}
    assert len(seen) == 1000


def test_tsv_roundtrip(tmp_path):
    pairs = [Pair("a\tb", "c"), Pair("hello", "dia\tduit")]
    f = tmp_path / "x.tsv"
    write_tsv(pairs, f)
    loaded = read_tsv(f)
    assert loaded == [Pair("a b", "c"), Pair("hello", "dia duit")]

import numpy as np
import pytest

try:
    from gaeilge_ai.router import features  # imports adaptive_weighted_models too
except Exception as e:
    pytest.skip(f"router unavailable: {e}", allow_module_level=True)


def test_features_shape_and_finiteness():
    f = features("Dia duit, conas atá tú?")
    assert f.shape == (7,)
    assert np.all(np.isfinite(f))


def test_features_fada_count():
    no_fada = features("Conas ata tu")
    with_fada = features("Conas atá tú")
    assert with_fada[-1] > no_fada[-1]

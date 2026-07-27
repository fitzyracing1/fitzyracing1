from gravity_feed_model import GravityFeedObservation, GravityFeedWeightedModel


def _synthetic_data() -> list[GravityFeedObservation]:
    # Ground truth: y = 0.8 + 2.2*sqrt(h) + 1.5*g + 0.7*d
    return [
        GravityFeedObservation(1.0, 0.2, 0.9, 0.8 + 2.2 * (1.0**0.5) + 1.5 * 0.2 + 0.7 * 0.9),
        GravityFeedObservation(2.25, 0.4, 1.1, 0.8 + 2.2 * (2.25**0.5) + 1.5 * 0.4 + 0.7 * 1.1),
        GravityFeedObservation(4.0, 0.6, 1.2, 0.8 + 2.2 * (4.0**0.5) + 1.5 * 0.6 + 0.7 * 1.2),
        GravityFeedObservation(6.25, 0.8, 1.0, 0.8 + 2.2 * (6.25**0.5) + 1.5 * 0.8 + 0.7 * 1.0),
        GravityFeedObservation(9.0, 0.3, 1.3, 0.8 + 2.2 * (9.0**0.5) + 1.5 * 0.3 + 0.7 * 1.3),
    ]


def test_fit_predict_recover_coefficients() -> None:
    model = GravityFeedWeightedModel()
    model.fit(_synthetic_data())

    assert abs(model.coefficients[0] - 0.8) < 1e-8
    assert abs(model.coefficients[1] - 2.2) < 1e-8
    assert abs(model.coefficients[2] - 1.5) < 1e-8
    assert abs(model.coefficients[3] - 0.7) < 1e-8


def test_predict_requires_fit() -> None:
    model = GravityFeedWeightedModel()
    try:
        model.predict(2.0, 0.5, 1.0)
        assert False, "expected RuntimeError"
    except RuntimeError:
        pass

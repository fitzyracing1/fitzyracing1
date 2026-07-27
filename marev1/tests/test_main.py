"""Tests for main module."""

from marev1.main import hello


def test_hello(capsys):
    """Test hello function."""
    hello()
    captured = capsys.readouterr()
    assert "Hello, World!" in captured.out

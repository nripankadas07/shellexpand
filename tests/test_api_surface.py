"""Smoke tests that pin down the public ``shellexpand`` API surface."""
from __future__ import annotations

import shellexpand


def test_api_surface_exposes_documented_callables() -> None:
    for name in (
        "expand",
        "expand_string",
        "expand_braces",
        "expand_tilde",
        "expand_parameter",
        "escape",
        "unescape",
        "is_valid_name",
        "resolve_home",
    ):
        assert callable(getattr(shellexpand, name)), name


def test_api_surface_exposes_error_classes() -> None:
    assert issubclass(shellexpand.ShellExpandError, ValueError)
    assert issubclass(shellexpand.BraceExpansionError, shellexpand.ShellExpandError)
    assert issubclass(shellexpand.UndefinedVariableError, shellexpand.ShellExpandError)


def test_api_surface_has_version() -> None:
    assert isinstance(shellexpand.__version__, str)
    assert shellexpand.__version__


def test_api_surface_all_lists_every_public_name() -> None:
    expected = {
        "expand",
        "expand_string",
        "expand_braces",
        "expand_tilde",
        "expand_parameter",
        "escape",
        "unescape",
        "is_valid_name",
        "resolve_home",
        "ShellExpandError",
        "BraceExpansionError",
        "UndefinedVariableError",
    }
    assert set(shellexpand.__all__) == expected


def test_is_valid_name_happy_and_edge_cases() -> None:
    assert shellexpand.is_valid_name("_foo")
    assert shellexpand.is_valid_name("FOO_123")
    assert shellexpand.is_valid_name("a")
    assert not shellexpand.is_valid_name("")
    assert not shellexpand.is_valid_name("1abc")
    assert not shellexpand.is_valid_name("a-b")
    assert not shellexpand.is_valid_name("a b")
    assert not shellexpand.is_valid_name("é")

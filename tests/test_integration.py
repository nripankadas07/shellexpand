"""End-to-end integration tests combining every expansion phase."""
from __future__ import annotations

import pytest

from shellexpand import expand, expand_string


def test_integration_path_template() -> None:
    env = {"USER": "alice", "PROJECT": "forge"}
    result = expand(
        "~/projects/$PROJECT/{src,tests}/$USER.log",
        env=env,
        home="/home/alice",
    )
    assert result == [
        "/home/alice/projects/forge/src/alice.log",
        "/home/alice/projects/forge/tests/alice.log",
    ]


def test_integration_range_with_default_word() -> None:
    result = expand(
        "host-{1..3}.${DOMAIN:-example.com}", env={}
    )
    assert result == [
        "host-1.example.com",
        "host-2.example.com",
        "host-3.example.com",
    ]


def test_integration_escape_keeps_brace_literal() -> None:
    assert expand(r"keep \{a,b\}") == ["keep {a,b}"]


def test_integration_strict_unset_in_branch() -> None:
    with pytest.raises(Exception):
        expand("{a,b}-$MISSING", env={}, strict=True)


def test_integration_expand_string_full_chain() -> None:
    assert (
        expand_string("~/$NAME/file", env={"NAME": "n"}, home="/h")
        == "/h/n/file"
    )


def test_integration_multiple_braces_cartesian() -> None:
    result = expand("{x,y}-{1,2}", env={})
    assert result == ["x-1", "x-2", "y-1", "y-2"]


def test_integration_quoted_dollar_kept_literal_via_escape() -> None:
    # Users wanting to keep a literal $ should escape it.
    assert expand(r"price: \$10", env={}) == ["price: $10"]


def test_integration_nested_braces_and_params() -> None:
    env = {"X": "alpha", "Y": "beta"}
    result = expand("{$X,{$Y,gamma}}", env=env)
    assert result == ["alpha", "beta", "gamma"]

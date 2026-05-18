"""Tests for the top-level :func:`expand` / :func:`expand_string` helpers."""
from __future__ import annotations

import pytest

from shellexpand import (
    UndefinedVariableError,
    expand,
    expand_string,
)


def test_expand_no_special_chars_returns_singleton() -> None:
    assert expand("plain") == ["plain"]


def test_expand_brace_then_tilde_then_param() -> None:
    result = expand(
        "~/{a,b}/$NAME", env={"NAME": "n"}, home="/h"
    )
    assert result == ["/h/a/n", "/h/b/n"]


def test_expand_string_does_not_split_braces() -> None:
    result = expand_string("~/${X}", env={"X": "v"}, home="/h")
    assert result == "/h/v"


def test_expand_string_keeps_brace_literal_via_no_split() -> None:
    # Note: expand_string still produces a single string. Brace markers
    # remain because no brace expansion runs.
    result = expand_string("{a,b}", env={})
    assert result == "{a,b}"


def test_expand_strict_propagates_undefined_error() -> None:
    with pytest.raises(UndefinedVariableError):
        expand("$X", env={}, strict=True)


def test_expand_unescape_strips_remaining_backslashes() -> None:
    assert expand(r"hello\!world") == ["hello!world"]


def test_expand_disable_unescape() -> None:
    assert expand(r"hello\!world", unescape_result=False) == [r"hello\!world"]


def test_expand_string_unescape_strips_remaining_backslashes() -> None:
    assert expand_string(r"a\b") == "ab"


def test_expand_string_disable_unescape() -> None:
    assert expand_string(r"a\b", unescape_result=False) == r"a\b"


def test_expand_uses_os_environ_when_env_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SHELLEXPAND_X", "yes")
    monkeypatch.setenv("HOME", "/h")
    assert expand("$SHELLEXPAND_X/~") == ["yes/~"]  # ~ only leading


def test_expand_tilde_only_leading_after_brace_split() -> None:
    # After brace expansion each word's leading ~ is expanded.
    assert expand("{~,plain}", home="/h") == ["/h", "plain"]


def test_expand_brace_range_with_params_inside_word() -> None:
    result = expand("file-{1..3}.$EXT", env={"EXT": "txt"})
    assert result == ["file-1.txt", "file-2.txt", "file-3.txt"]


def test_expand_default_strict_false_lets_unset_be_empty() -> None:
    assert expand("$MISSING", env={}) == [""]

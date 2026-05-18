"""Tests for the :func:`escape` / :func:`unescape` helpers."""
from __future__ import annotations

from shellexpand import escape, expand_string, unescape


def test_unescape_empty_string() -> None:
    assert unescape("") == ""


def test_unescape_strips_single_backslash() -> None:
    assert unescape(r"\a") == "a"


def test_unescape_preserves_trailing_backslash() -> None:
    # Trailing \ with no follow-on character is preserved verbatim.
    assert unescape("foo\\") == "foo\\"


def test_unescape_handles_double_backslash() -> None:
    # \\ -> \  (one removal)
    assert unescape(r"\\") == "\\"


def test_unescape_long_run_of_backslashes() -> None:
    # \\\\ -> \\  (pair-wise)
    assert unescape("\\\\\\\\") == "\\\\"


def test_unescape_plain_text_unchanged() -> None:
    assert unescape("no escapes here") == "no escapes here"


def test_escape_plain_text_unchanged() -> None:
    assert escape("abc123") == "abc123"


def test_escape_specials_get_backslashed() -> None:
    assert escape("a$b") == r"a\$b"
    assert escape("{a,b}") == r"\{a\,b\}"


def test_escape_preserves_unicode() -> None:
    assert escape("café") == "café"


def test_escape_then_expand_is_identity_for_specials() -> None:
    sample = "$VAR{a,b} ~"
    assert expand_string(escape(sample)) == sample


def test_escape_whitespace_is_escaped() -> None:
    # Backslash before space stops it from being a word separator.
    assert escape("a b") == r"a\ b"

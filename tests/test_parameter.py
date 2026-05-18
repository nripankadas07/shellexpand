"""Tests for parameter expansion."""
from __future__ import annotations

import pytest

from shellexpand import (
    ShellExpandError,
    UndefinedVariableError,
    expand_parameter,
)


def test_expand_parameter_no_dollar_returns_unchanged() -> None:
    assert expand_parameter("plain text") == "plain text"


def test_expand_parameter_empty_string() -> None:
    assert expand_parameter("") == ""


def test_expand_parameter_unbraced_lookup() -> None:
    assert expand_parameter("$NAME world", env={"NAME": "hi"}) == "hi world"


def test_expand_parameter_unbraced_greedy_stops_at_punct() -> None:
    assert expand_parameter("$FOO/bar", env={"FOO": "X"}) == "X/bar"


def test_expand_parameter_braced_simple() -> None:
    assert expand_parameter("${A}b", env={"A": "x"}) == "xb"


def test_expand_parameter_undefined_lenient_is_empty() -> None:
    assert expand_parameter("a$X b", env={}) == "a b"


def test_expand_parameter_undefined_strict_raises() -> None:
    with pytest.raises(UndefinedVariableError) as excinfo:
        expand_parameter("$X", env={}, strict=True)
    assert excinfo.value.name == "X"


def test_expand_parameter_default_when_unset() -> None:
    assert expand_parameter("${X:-def}", env={}) == "def"


def test_expand_parameter_default_when_empty() -> None:
    assert expand_parameter("${X:-def}", env={"X": ""}) == "def"


def test_expand_parameter_default_when_set_keeps_value() -> None:
    assert expand_parameter("${X:-def}", env={"X": "v"}) == "v"


def test_expand_parameter_dash_default_only_unset_not_empty() -> None:
    assert expand_parameter("${X-def}", env={"X": ""}) == ""
    assert expand_parameter("${X-def}", env={}) == "def"


def test_expand_parameter_alt_value_when_set_and_nonempty() -> None:
    assert expand_parameter("${X:+alt}", env={"X": "v"}) == "alt"


def test_expand_parameter_alt_value_when_empty_is_empty() -> None:
    assert expand_parameter("${X:+alt}", env={"X": ""}) == ""


def test_expand_parameter_plus_alt_treats_empty_as_set() -> None:
    assert expand_parameter("${X+alt}", env={"X": ""}) == "alt"


def test_expand_parameter_question_raises_with_word() -> None:
    with pytest.raises(UndefinedVariableError) as excinfo:
        expand_parameter("${X:?missing}", env={})
    assert "missing" in str(excinfo.value)
    assert excinfo.value.name == "X"


def test_expand_parameter_question_passes_when_set() -> None:
    assert expand_parameter("${X:?missing}", env={"X": "ok"}) == "ok"


def test_expand_parameter_equals_is_default_no_side_effect() -> None:
    # We don't mutate env (the library is functional), but the value is
    # still expanded as if :- had been used.
    env: dict[str, str] = {}
    assert expand_parameter("${X:=def}", env=env) == "def"
    assert env == {}


def test_expand_parameter_dollar_at_end_keeps_literal() -> None:
    assert expand_parameter("price: $", env={}) == "price: $"


def test_expand_parameter_dollar_before_digit_keeps_literal() -> None:
    assert expand_parameter("$9 saved", env={"_9": "no"}) == "$9 saved"


def test_expand_parameter_dollar_before_punct_keeps_literal() -> None:
    assert expand_parameter("$-foo", env={}) == "$-foo"


def test_expand_parameter_escape_dollar() -> None:
    assert expand_parameter(r"\$X", env={"X": "v"}) == "$X"


def test_expand_parameter_escape_backslash() -> None:
    assert expand_parameter(r"\\X", env={}) == r"\X"


def test_expand_parameter_unterminated_brace_raises() -> None:
    with pytest.raises(ShellExpandError):
        expand_parameter("${UNCLOSED", env={})


def test_expand_parameter_invalid_name_inside_braces_raises() -> None:
    with pytest.raises(ShellExpandError):
        expand_parameter("${1abc}", env={})


def test_expand_parameter_empty_braces_raise() -> None:
    with pytest.raises(ShellExpandError):
        expand_parameter("${}", env={})


def test_expand_parameter_defaults_to_os_environ(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SHELLEXPAND_TEST_VAR", "hello")
    assert expand_parameter("$SHELLEXPAND_TEST_VAR") == "hello"


def test_expand_parameter_question_no_word_default_message() -> None:
    with pytest.raises(UndefinedVariableError):
        expand_parameter("${X?}", env={})


def test_expand_parameter_nested_default_with_special_chars() -> None:
    # The default word can contain any characters except an unescaped close.
    assert expand_parameter("${X:-a:b-c}", env={}) == "a:b-c"


def test_expand_parameter_underscore_name() -> None:
    assert expand_parameter("$_X9", env={"_X9": "ok"}) == "ok"

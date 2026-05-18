"""Tests for brace expansion."""
from __future__ import annotations

import pytest

from shellexpand import BraceExpansionError, expand_braces


def test_expand_braces_no_braces_returns_singleton() -> None:
    assert expand_braces("abc") == ["abc"]


def test_expand_braces_empty_input() -> None:
    assert expand_braces("") == [""]


def test_expand_braces_comma_list_simple() -> None:
    assert expand_braces("{a,b,c}") == ["a", "b", "c"]


def test_expand_braces_with_prefix_and_suffix() -> None:
    assert expand_braces("pre{a,b}post") == ["preapost", "prebpost"]


def test_expand_braces_nested_groups() -> None:
    assert expand_braces("a{b,{c,d}}e") == ["abe", "ace", "ade"]


def test_expand_braces_two_groups_multiply() -> None:
    assert expand_braces("{a,b}-{1,2}") == ["a-1", "a-2", "b-1", "b-2"]


def test_expand_braces_empty_segment_kept() -> None:
    assert expand_braces("{a,,b}") == ["a", "", "b"]


def test_expand_braces_int_range_ascending() -> None:
    assert expand_braces("{1..3}") == ["1", "2", "3"]


def test_expand_braces_int_range_descending() -> None:
    assert expand_braces("{3..1}") == ["3", "2", "1"]


def test_expand_braces_int_range_with_step() -> None:
    assert expand_braces("{1..10..2}") == ["1", "3", "5", "7", "9"]


def test_expand_braces_int_range_negative_step_uses_abs() -> None:
    assert expand_braces("{1..5..-1}") == ["1", "2", "3", "4", "5"]


def test_expand_braces_int_range_with_signed_bound() -> None:
    assert expand_braces("{-1..1}") == ["-1", "0", "1"]


def test_expand_braces_char_range_ascending() -> None:
    assert expand_braces("{a..c}") == ["a", "b", "c"]


def test_expand_braces_char_range_descending() -> None:
    assert expand_braces("{Z..X}") == ["Z", "Y", "X"]


def test_expand_braces_char_range_with_step() -> None:
    assert expand_braces("{a..g..2}") == ["a", "c", "e", "g"]


def test_expand_braces_unbalanced_open_is_literal() -> None:
    assert expand_braces("{a,b") == ["{a,b"]


def test_expand_braces_unbalanced_after_balanced() -> None:
    assert expand_braces("{a,b}{c,d") == ["a{c,d", "b{c,d"]


def test_expand_braces_no_comma_no_range_is_literal() -> None:
    assert expand_braces("{abc}") == ["{abc}"]


def test_expand_braces_mixed_type_range_is_literal() -> None:
    # Bash treats {1..a} as literal — not a range.
    assert expand_braces("{1..a}") == ["{1..a}"]


def test_expand_braces_zero_step_raises() -> None:
    with pytest.raises(BraceExpansionError):
        expand_braces("{1..5..0}")


def test_expand_braces_non_int_step_raises() -> None:
    with pytest.raises(BraceExpansionError):
        expand_braces("{1..5..abc}")


def test_expand_braces_escaped_open_is_skipped() -> None:
    assert expand_braces(r"\{a,b}") == [r"\{a,b}"]


def test_expand_braces_escaped_comma_keeps_group_literal() -> None:
    assert expand_braces(r"{a\,b}") == [r"{a\,b}"]


def test_expand_braces_escaped_close_inside_group() -> None:
    # The literal close inside is escaped; outer braces still match.
    assert expand_braces(r"{a,b\}c}") == ["a", r"b\}c"]


def test_expand_braces_trailing_backslash_is_kept() -> None:
    assert expand_braces("foo\\") == ["foo\\"]


def test_expand_braces_long_dotdot_text_not_a_range() -> None:
    # Three or more separators are not a range.
    assert expand_braces("{1..2..3..4}") == ["{1..2..3..4}"]


def test_expand_braces_int_range_step_explicit_one() -> None:
    assert expand_braces("{1..3..1}") == ["1", "2", "3"]


def test_expand_braces_int_range_same_bounds() -> None:
    assert expand_braces("{5..5}") == ["5"]


def test_expand_braces_char_range_same_bounds() -> None:
    assert expand_braces("{a..a}") == ["a"]


def test_expand_braces_step_too_big_yields_just_start() -> None:
    assert expand_braces("{1..3..10}") == ["1"]


def test_expand_braces_empty_range_bound_is_literal() -> None:
    # Empty bound — not a valid range, falls through to literal.
    assert expand_braces("{1..}") == ["{1..}"]
    assert expand_braces("{..3}") == ["{..3}"]

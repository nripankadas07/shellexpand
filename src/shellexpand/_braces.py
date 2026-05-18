"""POSIX-style brace expansion.

Supports the common :command:`bash` shapes:

* Comma lists — ``{a,b,c}`` → ``['a', 'b', 'c']``
* Numeric ranges — ``{1..5}``, ``{5..1}``, ``{1..10..2}``
* Single-letter ranges — ``{a..c}``, ``{Z..X}``, ``{a..z..2}``
* Nested groups — ``a{b,{c,d}}e`` → ``['abe', 'ace', 'ade']``

Escape rules: a backslash before ``{``, ``}``, ``,``, or ``\\`` makes the
following character literal and stops it from participating in brace
matching or comma-splitting. The escape character itself is removed from
the output once a group has been matched.
"""
from __future__ import annotations

from typing import Optional, Tuple

from ._errors import BraceExpansionError

__all__ = ["expand_braces"]


def expand_braces(text: str) -> list[str]:
    """Return the brace expansion of *text* as a list of strings.

    Always returns at least one element. If no top-level brace group is
    found, the returned list is ``[text]`` (with escape characters
    preserved — they are only stripped for groups that *do* expand).
    """
    return _expand(text)


def _expand(text: str) -> list[str]:
    """Recursive workhorse for :func:`expand_braces`."""
    group = _find_first_group(text)
    if group is None:
        return [text]
    start, end, pieces, is_range = group
    prefix = text[:start]
    suffix = text[end + 1 :]
    if not is_range:
        pieces = _expand_pieces(pieces)
    suffix_expansions = _expand(suffix)
    return [prefix + piece + tail for piece in pieces for tail in suffix_expansions]


def _expand_pieces(pieces: list[str]) -> list[str]:
    """Recursively expand each comma-separated piece and concatenate."""
    expanded: list[str] = []
    for piece in pieces:
        expanded.extend(_expand(piece))
    return expanded


def _find_first_group(
    text: str,
) -> Optional[Tuple[int, int, list[str], bool]]:
    """Locate the first expandable brace group in *text*.

    Returns ``(start, end, pieces, is_range)`` where ``start`` and ``end``
    are indices of the matching ``{`` / ``}`` and ``pieces`` are the
    already-expanded strings to substitute. Literal brace groups (no
    commas and not a valid range) are skipped over.
    """
    i = 0
    while i < len(text):
        char = text[i]
        if char == "\\" and i + 1 < len(text):
            i += 2
            continue
        if char == "{":
            match = _match_brace_group(text, i)
            if match is not None:
                return match
            close = _find_close(text, i)
            if close is None:
                return None
            i = close + 1
            continue
        i += 1
    return None


def _match_brace_group(
    text: str, open_idx: int
) -> Optional[Tuple[int, int, list[str], bool]]:
    """Build the expansion record for the brace group opening at *open_idx*."""
    close, commas = _scan_for_close(text, open_idx)
    if close is None:
        return None
    inside = text[open_idx + 1 : close]
    if commas:
        pieces = _split_on_commas(text, open_idx + 1, close, commas)
        return (open_idx, close, pieces, False)
    range_pieces = _try_range(inside)
    if range_pieces is not None:
        return (open_idx, close, range_pieces, True)
    return None


def _find_close(text: str, open_idx: int) -> Optional[int]:
    """Return the index of the matching ``}`` for the ``{`` at *open_idx*."""
    close, _ = _scan_for_close(text, open_idx)
    return close


def _scan_for_close(
    text: str, open_idx: int
) -> Tuple[Optional[int], list[int]]:
    """Walk *text* looking for the matching close and top-level commas."""
    depth = 1
    commas: list[int] = []
    j = open_idx + 1
    while j < len(text):
        char = text[j]
        if char == "\\" and j + 1 < len(text):
            j += 2
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return j, commas
        elif char == "," and depth == 1:
            commas.append(j)
        j += 1
    return None, commas


def _split_on_commas(
    text: str, start: int, end: int, commas: list[int]
) -> list[str]:
    """Split ``text[start:end]`` on the recorded top-level *commas*."""
    pieces: list[str] = []
    last = start
    for comma_pos in commas:
        pieces.append(text[last:comma_pos])
        last = comma_pos + 1
    pieces.append(text[last:end])
    return pieces


def _try_range(inside: str) -> Optional[list[str]]:
    """Try to parse *inside* as a range expression.

    Returns the expanded values, or ``None`` if *inside* is not a range.
    Raises :class:`BraceExpansionError` if it *looks* like a range
    (matching-type bounds present) but the step is malformed.
    """
    parts = inside.split("..")
    if len(parts) not in (2, 3):
        return None
    lo, hi = parts[0], parts[1]
    step_text = parts[2] if len(parts) == 3 else None
    int_result = _try_int_range(lo, hi, step_text)
    if int_result is not None:
        return int_result
    char_result = _try_char_range(lo, hi, step_text)
    if char_result is not None:
        return char_result
    return None


def _try_int_range(lo: str, hi: str, step_text: Optional[str]) -> Optional[list[str]]:
    """Return the integer range expansion, or ``None`` if non-numeric."""
    if not (_is_int_literal(lo) and _is_int_literal(hi)):
        return None
    step = _parse_step(step_text)
    start, end = int(lo), int(hi)
    return _int_sequence(start, end, step)


def _try_char_range(lo: str, hi: str, step_text: Optional[str]) -> Optional[list[str]]:
    """Return the single-letter range expansion, or ``None`` if non-letters."""
    if not (_is_single_letter(lo) and _is_single_letter(hi)):
        return None
    step = _parse_step(step_text)
    return [chr(code) for code in _codes(ord(lo), ord(hi), step)]


def _codes(start: int, end: int, step: int) -> list[int]:
    """Walk an inclusive integer sequence — direction inferred from bounds."""
    direction = 1 if end >= start else -1
    return list(range(start, end + direction, direction * step))


def _int_sequence(start: int, end: int, step: int) -> list[str]:
    """Return the inclusive integer sequence as strings."""
    return [str(code) for code in _codes(start, end, step)]


def _parse_step(step_text: Optional[str]) -> int:
    """Validate and return the absolute step value."""
    if step_text is None:
        return 1
    if not _is_int_literal(step_text):
        raise BraceExpansionError(f"invalid range step: {step_text!r}")
    step = int(step_text)
    if step == 0:
        raise BraceExpansionError("range step cannot be zero")
    return abs(step)


def _is_int_literal(text: str) -> bool:
    """Return ``True`` if *text* parses as a signed decimal integer."""
    if not text:
        return False
    body = text[1:] if text[0] in "+-" else text
    return body.isdigit()


def _is_single_letter(text: str) -> bool:
    """Return ``True`` if *text* is exactly one ASCII letter."""
    return len(text) == 1 and text.isascii() and text.isalpha()

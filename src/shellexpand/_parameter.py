"""POSIX-style parameter (variable) expansion.

Handles the common forms:

* ``$VAR`` — unbraced reference, runs of valid identifier characters.
* ``${VAR}`` — braced reference, identifier only.
* ``${VAR:-word}`` — *word* when ``VAR`` is unset or empty.
* ``${VAR-word}``  — *word* when ``VAR`` is unset (empty kept).
* ``${VAR:+word}`` — *word* when ``VAR`` is set and non-empty.
* ``${VAR+word}``  — *word* when ``VAR`` is set (even if empty).
* ``${VAR:=word}`` — like ``${VAR:-word}`` (the assignment side-effect of
  the shell is **not** performed; this library is functional).
* ``${VAR:?msg}`` — raise :class:`UndefinedVariableError` with *msg*
  when ``VAR`` is unset or empty.

A backslash before ``$`` (``\\$``) or before ``\\`` itself (``\\\\``)
escapes the special meaning; the escape is removed on output.
"""
from __future__ import annotations

import os
from typing import Mapping, Optional

from ._errors import ShellExpandError, UndefinedVariableError
from ._names import is_valid_name

__all__ = ["expand_parameter"]


_NAME_BODY = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")


def expand_parameter(
    text: str, *, env: Optional[Mapping[str, str]] = None, strict: bool = False
) -> str:
    """Expand ``$VAR`` / ``${VAR...}`` references inside *text*.

    *env* — mapping to look variables up in. ``None`` falls back to
    :data:`os.environ` so that the helper is useful out of the box.

    *strict* — when ``True``, every reference to an unset variable raises
    :class:`UndefinedVariableError`; otherwise the unset value is treated
    as the empty string (consistent with :command:`bash`).
    """
    lookup = os.environ if env is None else env
    out: list[str] = []
    i = 0
    while i < len(text):
        char = text[i]
        if char == "\\" and i + 1 < len(text) and text[i + 1] in "\\$":
            out.append(text[i + 1])
            i += 2
            continue
        if char != "$":
            out.append(char)
            i += 1
            continue
        value, consumed = _read_reference(text, i, lookup, strict)
        out.append(value)
        i += consumed
    return "".join(out)


def _read_reference(
    text: str, idx: int, env: Mapping[str, str], strict: bool
) -> tuple[str, int]:
    """Parse a single ``$`` reference starting at *idx*.

    Returns ``(value, consumed)`` where *consumed* is the number of source
    characters that were eaten. A trailing ``$`` (at end-of-text) is kept
    as a literal ``$`` and consumes one character.
    """
    if idx + 1 >= len(text):
        return "$", 1
    follow = text[idx + 1]
    if follow == "{":
        return _read_braced(text, idx, env, strict)
    if follow in _NAME_BODY and not follow.isdigit():
        return _read_unbraced(text, idx, env, strict)
    return "$", 1


def _read_unbraced(
    text: str, idx: int, env: Mapping[str, str], strict: bool
) -> tuple[str, int]:
    """Read an unbraced ``$NAME`` reference; greedy on identifier characters."""
    end = idx + 1
    while end < len(text) and text[end] in _NAME_BODY:
        end += 1
    name = text[idx + 1 : end]
    return _lookup(env, name, strict), end - idx


def _read_braced(
    text: str, idx: int, env: Mapping[str, str], strict: bool
) -> tuple[str, int]:
    """Read a ``${...}`` reference, honoring the supported operator suffixes."""
    close = text.find("}", idx + 2)
    if close == -1:
        raise ShellExpandError(f"unterminated ${{ at index {idx}")
    body = text[idx + 2 : close]
    name, operator, word = _split_body(body)
    if not is_valid_name(name):
        raise ShellExpandError(f"invalid variable name: {name!r}")
    consumed = close - idx + 1
    value = _apply_operator(env, name, operator, word, strict)
    return value, consumed


def _split_body(body: str) -> tuple[str, str, str]:
    """Split ``NAME[op WORD]`` into its three pieces."""
    for marker in (":-", ":=", ":?", ":+", "-", "=", "?", "+"):
        idx = body.find(marker)
        if idx > 0:
            return body[:idx], marker, body[idx + len(marker) :]
    return body, "", ""


def _apply_operator(
    env: Mapping[str, str], name: str, operator: str, word: str, strict: bool
) -> str:
    """Resolve ``${name op word}`` against *env*."""
    if operator == "":
        return _lookup(env, name, strict)
    is_set = name in env
    value = env.get(name, "")
    treat_empty_as_unset = operator.startswith(":")
    unset = (not is_set) or (treat_empty_as_unset and value == "")
    if operator in (":-", "-", ":=", "="):
        return word if unset else value
    if operator in (":+", "+"):
        return "" if unset else word
    return _apply_error_op(name, value, unset, word)


def _apply_error_op(name: str, value: str, unset: bool, word: str) -> str:
    """Handle the ``${VAR:?msg}`` / ``${VAR?msg}`` form."""
    if unset:
        raise UndefinedVariableError(name, word or None)
    return value


def _lookup(env: Mapping[str, str], name: str, strict: bool) -> str:
    """Plain lookup with optional strict-mode raise."""
    if name in env:
        return env[name]
    if strict:
        raise UndefinedVariableError(name)
    return ""

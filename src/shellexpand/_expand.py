"""Top-level orchestrator combining brace, tilde, and parameter expansion."""
from __future__ import annotations

from typing import Mapping, Optional

from ._braces import expand_braces
from ._parameter import expand_parameter
from ._tilde import expand_tilde

__all__ = ["expand", "expand_string", "unescape", "escape"]


_SHELL_SPECIALS = frozenset("\\${}~,*?[]| <>&;()`\"'\t\n")


def expand(
    text: str,
    *,
    env: Optional[Mapping[str, str]] = None,
    home: Optional[str] = None,
    strict: bool = False,
    unescape_result: bool = True,
) -> list[str]:
    """Apply brace, tilde, and parameter expansion to *text*.

    Behaviour mirrors :command:`bash`'s ordering: brace expansion runs first
    (and may multiply the word count), then tilde, then parameter expansion
    are applied to each resulting word.

    *env* — variable lookup table (defaults to :data:`os.environ`).
    *home* — value substituted for ``~`` (defaults to ``$HOME`` then OS).
    *strict* — raise :class:`UndefinedVariableError` for unset variables.
    *unescape_result* — strip leading ``\\`` from any ``\\X`` pairs that
    survive expansion (matches bash's "quote removal" step).
    """
    words = expand_braces(text)
    return [
        _finish_word(word, home=home, env=env, strict=strict, do_unescape=unescape_result)
        for word in words
    ]


def expand_string(
    text: str,
    *,
    env: Optional[Mapping[str, str]] = None,
    home: Optional[str] = None,
    strict: bool = False,
    unescape_result: bool = True,
) -> str:
    """Like :func:`expand`, but skips brace expansion and returns a string.

    Useful for callers that want to expand a single template (e.g. a
    configuration value) without ever producing multiple words.
    """
    return _finish_word(
        text, home=home, env=env, strict=strict, do_unescape=unescape_result
    )


def _finish_word(
    word: str,
    *,
    home: Optional[str],
    env: Optional[Mapping[str, str]],
    strict: bool,
    do_unescape: bool,
) -> str:
    """Apply tilde → parameter → optional unescape to a single word."""
    word = expand_tilde(word, home=home)
    word = expand_parameter(word, env=env, strict=strict)
    if do_unescape:
        word = unescape(word)
    return word


def unescape(text: str) -> str:
    """Strip a single leading backslash from every ``\\X`` pair.

    This mirrors :command:`bash`'s "quote removal" step: any backslash is
    consumed and the following character is preserved literally. A trailing
    backslash (no following character) is kept as-is so input is never
    silently truncated.
    """
    out: list[str] = []
    i = 0
    while i < len(text):
        char = text[i]
        if char == "\\" and i + 1 < len(text):
            out.append(text[i + 1])
            i += 2
            continue
        out.append(char)
        i += 1
    return "".join(out)


def escape(text: str) -> str:
    """Backslash-escape every shell-special character in *text*.

    The result is safe to pass through :func:`expand` and round-trip back
    to the original. Whitespace, quotes, brackets, braces, ``$``, ``~``,
    pipes, and glob metacharacters are all escaped.
    """
    out: list[str] = []
    for char in text:
        if char in _SHELL_SPECIALS:
            out.append("\\")
        out.append(char)
    return "".join(out)

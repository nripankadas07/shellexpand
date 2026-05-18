"""Tilde expansion.

A leading ``~`` followed by end-of-string or ``/`` is replaced with the
caller-supplied home directory (defaulting to ``$HOME`` then to the OS
notion of the current user's home). ``~user`` lookup is intentionally
**not** supported — it would require the ``pwd`` module and platform
calls, which we exclude for the sake of being a zero-dep library.

A backslash-escaped tilde (``\\~``) is preserved literally. Tildes that
appear anywhere other than at the start of the string (or at the start of
a colon-separated PATH-like segment) are also left alone.
"""
from __future__ import annotations

import os
from typing import Optional

__all__ = ["expand_tilde", "resolve_home"]


def resolve_home(home: Optional[str] = None) -> str:
    """Return the home directory to substitute for ``~``.

    The lookup order is: explicit *home* argument, ``$HOME`` environment
    variable, and :func:`os.path.expanduser` as the OS-aware fallback.
    """
    if home is not None:
        return home
    env_home = os.environ.get("HOME")
    if env_home is not None:
        return env_home
    return os.path.expanduser("~")


def expand_tilde(text: str, *, home: Optional[str] = None) -> str:
    """Expand a single leading ``~`` token in *text*.

    Only the leading ``~`` is considered: any ``~`` later in the string is
    returned unchanged. A backslash directly before ``~`` (``\\~``) is
    stripped and the ``~`` is preserved literally.
    """
    if not text:
        return text
    if text.startswith("\\~"):
        return "~" + text[2:]
    if text[0] != "~":
        return text
    if len(text) == 1 or text[1] == "/":
        return resolve_home(home) + text[1:]
    return text

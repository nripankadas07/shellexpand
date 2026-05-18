"""Identifier validation helpers shared by parameter expansion."""
from __future__ import annotations

__all__ = ["is_valid_name"]


def is_valid_name(name: str) -> bool:
    """Return ``True`` if *name* is a valid POSIX shell identifier.

    The rules match :command:`bash` / POSIX: the name must be non-empty, the
    first character must be an ASCII letter or underscore, and every
    remaining character must be an ASCII letter, digit, or underscore.
    """
    if not name:
        return False
    head = name[0]
    if not (head.isascii() and (head.isalpha() or head == "_")):
        return False
    for char in name[1:]:
        if not (char.isascii() and (char.isalnum() or char == "_")):
            return False
    return True

"""Exception hierarchy for :mod:`shellexpand`."""
from __future__ import annotations

__all__ = [
    "ShellExpandError",
    "BraceExpansionError",
    "UndefinedVariableError",
]


class ShellExpandError(ValueError):
    """Base class for every error raised by :mod:`shellexpand`.

    Subclasses :class:`ValueError` because every failure during expansion is a
    problem with the *value* of the input string. Catching :class:`ValueError`
    is therefore sufficient for callers that only care about "did expansion
    work?".
    """


class BraceExpansionError(ShellExpandError):
    """Raised when a brace group has a malformed numeric range.

    Examples include an empty step, a step of zero, or a step that is not a
    decimal integer. Unbalanced ``{`` / ``}`` pairs and non-range literal
    groups (for instance ``{abc}``) are *not* errors — they are left in the
    output verbatim to match :command:`bash` behaviour.
    """


class UndefinedVariableError(ShellExpandError):
    """Raised when ``strict=True`` and a referenced variable is unset.

    The attribute :attr:`name` holds the offending variable name so callers
    can build user-facing diagnostics without re-parsing the message.
    """

    def __init__(self, name: str, message: str | None = None) -> None:
        super().__init__(message or f"undefined variable: {name!r}")
        self.name = name

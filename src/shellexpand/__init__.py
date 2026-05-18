"""shellexpand — zero-dep POSIX-style shell text expansion.

Public API:

* :func:`expand` — brace + tilde + parameter expansion, returning a list of
  words (bash-style).
* :func:`expand_string` — same minus brace expansion, returning a string.
* :func:`expand_braces` — brace expansion only.
* :func:`expand_tilde` — tilde expansion only.
* :func:`expand_parameter` — ``$VAR`` / ``${VAR:-d}`` expansion only.
* :func:`escape` / :func:`unescape` — quote removal helpers.
* :func:`is_valid_name` — identifier validator.

Error tree (all subclass :class:`ValueError`):

* :class:`ShellExpandError` — base class.
* :class:`BraceExpansionError` — malformed brace range step.
* :class:`UndefinedVariableError` — strict-mode unset variable.
"""
from __future__ import annotations

from ._braces import expand_braces
from ._errors import (
    BraceExpansionError,
    ShellExpandError,
    UndefinedVariableError,
)
from ._expand import escape, expand, expand_string, unescape
from ._names import is_valid_name
from ._parameter import expand_parameter
from ._tilde import expand_tilde, resolve_home

__all__ = [
    "expand",
    "expand_string",
    "expand_braces",
    "expand_tilde",
    "expand_parameter",
    "escape",
    "unescape",
    "is_valid_name",
    "resolve_home",
    "ShellExpandError",
    "BraceExpansionError",
    "UndefinedVariableError",
]

__version__ = "0.1.0"

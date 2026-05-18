"""Tests for tilde expansion."""
from __future__ import annotations

import os

import pytest

from shellexpand import expand_tilde, resolve_home


def test_expand_tilde_replaces_leading_tilde() -> None:
    assert expand_tilde("~", home="/h") == "/h"


def test_expand_tilde_with_slash_path() -> None:
    assert expand_tilde("~/foo/bar", home="/h") == "/h/foo/bar"


def test_expand_tilde_preserves_user_named_form_unchanged() -> None:
    # ~alice is not expanded — pwd-based lookup is intentionally out of scope.
    assert expand_tilde("~alice/foo", home="/h") == "~alice/foo"


def test_expand_tilde_no_leading_tilde_returns_unchanged() -> None:
    assert expand_tilde("/etc/passwd", home="/h") == "/etc/passwd"


def test_expand_tilde_escape_preserves_literal() -> None:
    assert expand_tilde("\\~/foo", home="/h") == "~/foo"


def test_expand_tilde_empty_string() -> None:
    assert expand_tilde("", home="/h") == ""


def test_expand_tilde_only_replaces_leading_token() -> None:
    assert expand_tilde("a~b", home="/h") == "a~b"


def test_resolve_home_uses_explicit_arg_first() -> None:
    assert resolve_home("/explicit") == "/explicit"


def test_resolve_home_falls_back_to_env_home(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HOME", "/from-env")
    assert resolve_home() == "/from-env"


def test_resolve_home_falls_back_to_os_when_env_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("HOME", raising=False)
    # Some platforms set USERPROFILE / HOMEDRIVE instead — just ensure non-empty.
    result = resolve_home()
    assert isinstance(result, str)
    # When HOME is absent expanduser may still expand on Unix using pwd; never raises.
    assert result == os.path.expanduser("~")


def test_expand_tilde_default_home_uses_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HOME", "/env-home")
    assert expand_tilde("~/x") == "/env-home/x"

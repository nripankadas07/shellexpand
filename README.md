# shellexpand

Zero-dep, type-checked, POSIX-style shell text expansion for Python — tilde,
brace, and parameter (`$VAR`, `${VAR:-default}`) expansion with escape
handling and a clean error tree.

```python
>>> import shellexpand
>>> shellexpand.expand("~/projects/{src,tests}/$USER.log",
...                    env={"USER": "alice"}, home="/home/alice")
['/home/alice/projects/src/alice.log',
 '/home/alice/projects/tests/alice.log']
```

* **Zero runtime dependencies** — pure standard library.
* **`mypy --strict` clean** — every public function has a complete type
  signature and `py.typed` ships in the wheel.
* **100% statement + branch coverage** — 108 tests covering happy path
  and edge cases on Python 3.10 / 3.11 / 3.12.
* **No globals, no surprises** — `${VAR:=default}` does **not** mutate
  the environment; the library is purely functional.

## Install

```
python -m pip install -e .
```

## Quick reference

| Function                          | Returns       | Phases applied                  |
|-----------------------------------|---------------|---------------------------------|
| `expand(text, **opts)`            | `list[str]`   | brace → tilde → parameter       |
| `expand_string(text, **opts)`     | `str`         | tilde → parameter               |
| `expand_braces(text)`             | `list[str]`   | brace only                      |
| `expand_tilde(text, home=None)`   | `str`         | tilde only                      |
| `expand_parameter(text, env=None, strict=False)` | `str` | parameter only           |
| `escape(text)` / `unescape(text)` | `str`         | quote-removal helpers           |
| `is_valid_name(name)`             | `bool`        | identifier validation           |

All keyword arguments are documented below.

## What gets expanded

### Brace expansion

```python
>>> shellexpand.expand_braces("file-{1..3}.txt")
['file-1.txt', 'file-2.txt', 'file-3.txt']
>>> shellexpand.expand_braces("{a,b}-{1,2}")
['a-1', 'a-2', 'b-1', 'b-2']
>>> shellexpand.expand_braces("{Z..X}")
['Z', 'Y', 'X']
>>> shellexpand.expand_braces("{a..g..2}")
['a', 'c', 'e', 'g']
```

Supported forms: comma lists `{a,b,c}`, nested groups `{a,{b,c}}`,
integer ranges with optional step `{1..10..2}`, and single-letter
ranges. Reversed bounds (e.g. `{3..1}`) auto-detect direction. Unbalanced
or non-range literal groups (`{abc}`, `{a,b`) are returned verbatim to
match `bash` behaviour. A zero or non-integer step raises
`BraceExpansionError`.

### Tilde expansion

```python
>>> shellexpand.expand_tilde("~/src", home="/home/alice")
'/home/alice/src'
```

Only a leading `~` (followed by end-of-string or `/`) is replaced. The
`~user` form is intentionally **not** supported — looking up other
users' homes would require `pwd` and platform-specific calls, which
this library avoids on purpose.

### Parameter expansion

```python
>>> shellexpand.expand_parameter("greeting: $NAME!", env={"NAME": "world"})
'greeting: world!'
>>> shellexpand.expand_parameter("${HOST:-localhost}", env={})
'localhost'
>>> shellexpand.expand_parameter("$X", env={}, strict=True)
Traceback (most recent call last):
  ...
shellexpand.UndefinedVariableError: undefined variable: 'X'
```

Supported operators inside `${...}`:

| Form           | Meaning                                           |
|----------------|---------------------------------------------------|
| `${VAR}`       | Plain lookup.                                     |
| `${VAR:-word}` | *word* when `VAR` is unset **or** empty.          |
| `${VAR-word}`  | *word* when `VAR` is unset (empty kept).          |
| `${VAR:+word}` | *word* when `VAR` is set and non-empty.           |
| `${VAR+word}`  | *word* when `VAR` is set (empty counts as set).   |
| `${VAR:=word}` | Like `:-` (no side-effect on *env*).              |
| `${VAR:?msg}`  | Raise `UndefinedVariableError(msg)` when unset.   |

### Escape and `unescape`

```python
>>> shellexpand.expand(r"keep \{a,b\}")
['keep {a,b}']
>>> shellexpand.escape("a $b {c,d}")
'a\\ \\$b\\ \\{c\\,d\\}'
```

`escape` backslash-quotes every shell-special character; `unescape`
applies the inverse "quote-removal" step that `bash` runs after every
expansion phase. The top-level `expand` / `expand_string` apply it by
default; pass `unescape_result=False` to opt out.

## Error tree

```
ValueError
 └── ShellExpandError
      ├── BraceExpansionError       # zero / non-integer range step
      └── UndefinedVariableError    # strict-mode unset variable
```

`UndefinedVariableError` carries the offending name in
`error.name` so callers can build structured diagnostics.

## Non-goals

* **Command substitution** (`$(...)` or backticks) — out of scope.
* **Arithmetic expansion** (`$(( ))`) — out of scope.
* **Glob / pathname expansion** — use a dedicated globber.
* **`~user` lookup** — would require the `pwd` module.
* **Word splitting on whitespace** — pass the result of `expand` to
  `shlex.split` if you need that on top.

## Running the tests

```
pip install pytest pytest-cov mypy
pytest --cov=shellexpand --cov-branch --cov-report=term-missing
mypy --strict src/shellexpand
```

Coverage target: **100% line + 100% branch** across all seven source
modules. Type-checking target: zero diagnostics with `mypy --strict`.

## License

MIT. See [`LICENSE`](LICENSE).

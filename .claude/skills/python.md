---
description: Python coding standards for this project
paths: "**/*.py"
---

# Python Standards

## Module structure
- Gerund naming for function-first modules (`_reading.py`, `_pivoting.py`, `_computing.py`, `_writing.py`)
- No class with a single non-init method — use a plain function instead
- `read`/`write` when I/O and serialization are coupled (CSV, GeoJSON); `load`/`dump` when serialization is decoupled from I/O (e.g. `json.loads` on an in-memory string)
- Verb-first function names — non-negotiable
- Avoid long monolithic modules — split proactively into small, focused modules. The right shape depends on the problem; don't force a cookie-cutter structure.

## Logging
- `logger = logging.getLogger(__name__)` at module level in every module that logs
- `logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")` only in `main.py` entry points — never in library modules

## Style
- f-strings for interpolation — no `%` formatting
- Intermediate assignments over nested calls — `a = f(x); b = g(a)` not `b = g(f(x))`. Chaining methods on a single object is fine (`df.groupby(...).sum().reset_index()`); nesting independent function calls is not.

## Imports
- Absolute imports from the top-level package — no relative imports
- No magic string used more than once — extract to a constant

## Constants
- `StrEnum` with `auto()` for categorical values used as string fragments (column names, keys)
- `dict[str, MyEnum]` only when the raw string doesn't map cleanly to the enum by name
- Constants live in dedicated `constants/` modules when shared across modules; single-module constants stay as private module-level variables
- When a dict defines the canonical set of keys, don't create a parallel set/list — use `dict.keys()` or `key in dict` directly

## Docstrings and comments
- Code should be self-documenting — docstrings are a last resort
- Add a docstring when the operation is non-trivial and the signature alone doesn't convey intent
- Include an `Example:` section only for non-trivial operations
- Applies equally to public functions and private helpers — the bar is the complexity of the operation, not its visibility
- Google format
- During refactors: review every comment and docstring at the destination — carry it over if still valid, update it if partially stale, add one if the move introduces non-obvious context. Don't move code naked.

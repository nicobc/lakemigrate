---
description: Python unit testing standards for this project
paths: "**/tests/**/*.py, **/conftest.py"
---

# Python Testing Standards

## Philosophy

Test behavior, not implementation details. A test earns its place when it verifies what a unit does, not how it does it. Exception: logic that can't be read off the surface (e.g. non-trivial recursion, complex stateful computation) may warrant a test as executable documentation — use judgment.

Test the highest-level public entrypoints that can still be considered independent units: public members of modules imported in `main`, or `main` itself. Everything beneath is an implementation detail unless independently complex.

When something is independently complex, the right response is design, not testing: extract the logic into a separate public pure function and test that. Never test I/O functions (readers, loaders, writers) — they contain no logic by definition. If one does, that logic belongs in a pure function instead.

If isolating a unit requires heroics (deep monkeypatching, filesystem gymnastics), that's a design smell — the unit has too many external dependencies baked in. Fix the design, don't paper over it with mocks.

If arrange is dominated by mocks and the underlying code isn't smelly, you're likely writing an integration test. That's a different concern — don't conflate.

## What not to test

- Private helpers (`_foo`)
- I/O functions (readers, loaders, writers)
- Third-party library behavior
- Framework glue

## Tooling

Pure pytest only. No `unittest`, no `TestCase`, no `self`, no `unittest.mock`.

## Structure

### File location

```
root/toplevelpackage/package/module.py
→ root/tests/unit/test_package_module.py
```

Flat naming under `tests/unit/` avoids pytest crashes from duplicate filenames across packages. Never add `__init__.py` to test directories — pytest discovers tests without them.

### No test classes — only functions

### Test function anatomy

```python
# Arrange via fixture injection and decorators. Minimize arrange in the test body.
# Fixtures defined in conftest.py. Reuse and combine fixtures to build scenarios.

@pytest.mark.usefixtures("...")  # side-effect fixtures that don't return a value (writer, db initializer, etc.)
@pytest.mark.parametrize("input_x, expected_y", [...], ids=[...])  # multi-scenario input|output injection; use input_* / expected_* naming and clean ids
def test_function_name(fixture_a, fixture_b, input_x, expected_y):
    # Act — finish constructing inputs if needed; call the unit under test
    actual_output = function_under_test(input_x, fixture_a)

    # Assert — assert on instance equality, not individual attributes.
    # Never transform actual_* before asserting — it masks bugs at the source.
    # Discrepancies between actual and expected must be fixed at the origin: either
    # the unit under test is wrong, or the expected fixture is wrong.
    assert actual_output == expected_output
```

For exceptions:
```python
with pytest.raises(SomeError):
    function_under_test(bad_input)
```

For side effects (write → read → assert). Prefer this sparingly — heavy use is a smell.

For schema/relation existence: assert the db object exists directly.

## Naming conventions

```yaml
test_function: test_<unit>                        # test_compute_avg_order_value
parametrize_input: input_<name>                   # input_orders
parametrize_expected: expected_<name>             # expected_avg
act_result: actual_<name>                         # actual_avg
parametrize_ids: expressive                       # "zero_orders", "single_customer" — not "0", "1"
factory_fixture: make_<thing>                     # make_customer
writer_fixture: write_<thing>                     # write_orders
initializer_fixture: initialize_<thing>           # initialize_db
scenario_fixture: <fixture>_<scenario>            # orders_empty, orders_single_customer
```

## Type hints

Type-hint everything: fixture return types, test function parameters, `parametrize` values. No exceptions.

```python
@pytest.fixture
def customer() -> Customer:
    return Customer(id=1, name="Meridian")

def test_compute_avg_order_value(customer: Customer, expected_avg: float) -> None:
    actual_avg = compute_avg_order_value(customer)
    assert actual_avg == expected_avg
```

`-> None` on all test functions. Factory fixtures return `Callable[..., T]`.

## Fixtures

All fixtures in `conftest.py`. Scope to minimize suite runtime.

Default to one combined fixture per unit under test. A single fixture that exercises multiple behaviors (e.g. null handling, cutoff logic, multiple records) is preferable to separate scenario fixtures. Use named scenario fixtures (`fixture_scenario`) only when behaviors are mutually exclusive or a combined fixture would be misleading.

```yaml
factory:         returns a callable that creates instances with varied arguments during arrange
side_effect:     sets up/tears down external state (db, file); inject via usefixtures
tmp_path:        any path-related I/O
monkeypatch:     patching boundaries (env vars, imported names, connect calls); presence should prompt a question about design
request.param:   preferred for parametrize-driven fixture selection
request.getfixturevalue: dynamic fixture lookup by name; pair with fixture_name_scenario_name naming pattern
```

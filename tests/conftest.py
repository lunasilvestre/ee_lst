"""Shared fixtures and call-graph helpers.

Earth Engine objects are lazy graph builders: `image.select("B").multiply(2)`
sends nothing anywhere, it just describes work for the server to do later.
That means the interesting, regression-prone part of this library - which band
it picks, which scale factor it applies, what it names the output - is fully
observable from the calls it makes, with no credentials and no network.

So every test here passes a MagicMock where an ee.Image would go and asserts on
the resulting call graph.
"""

import pytest
from unittest.mock import MagicMock


@pytest.fixture
def image():
    """Stand-in for an ee.Image."""
    return MagicMock(name="image")


def calls_to(mock, method):
    """Every call to `method` anywhere in `mock`'s call tree, as (args, kwargs).

    Matching on the final attribute name finds a call however deep it is
    chained, so `image.expression().where().where().rename("FVC")` is reported
    the same as a bare `image.rename("FVC")`. Without this the assertions would
    encode the exact chain shape and break on any harmless refactor.
    """
    found = []
    for name, args, kwargs in mock.mock_calls:
        if name and name.split(".")[-1] == method:
            found.append((args, kwargs))
    return found


def _strings_passed_to(mock, method):
    names = []
    for args, _ in calls_to(mock, method):
        for arg in args:
            if isinstance(arg, str):
                names.append(arg)
            elif isinstance(arg, (list, tuple)):
                names.extend(a for a in arg if isinstance(a, str))
    return names


def renamed_bands(*mocks):
    """Band names passed to any .rename() across the given mocks."""
    return [n for m in mocks for n in _strings_passed_to(m, "rename")]


def selected_bands(*mocks):
    """Band names passed to any .select(), flattening list arguments."""
    return [n for m in mocks for n in _strings_passed_to(m, "select")]


def expressions(mock):
    """Every .expression(formula, bindings) call, as a list of (formula, bindings)."""
    out = []
    for args, kwargs in calls_to(mock, "expression"):
        formula = args[0] if args else kwargs.get("expression")
        bindings = args[1] if len(args) > 1 else kwargs.get("opt_map") or {}
        out.append((formula, bindings))
    return out


def numeric_args(mock, method):
    """Every int/float passed to `method` anywhere in the call tree."""
    vals = []
    for args, _ in calls_to(mock, method):
        vals.extend(a for a in args if isinstance(a, (int, float)))
    return vals

"""Every Earth Engine name this library calls must exist on the real `ee`.

The rest of the suite mocks `ee`, which is what makes it fast and credential-free
- but a MagicMock answers to *any* attribute name, including ones upstream has
deleted. That blind spot hid a real breakage: `initialize_ee()` guarded on
`ee.data._initialized`, which earthengine-api removed, so the public entry point
raised AttributeError before doing anything. Every mocked test still passed.

These tests import the real earthengine-api and check only that the names exist
and have the right shape. No credentials, no network, no calls that reach the
service.
"""

import ee
import ee.data
import pytest


def test_initialisation_guard_exists():
    # What initialize_ee() branches on.
    assert hasattr(
        ee.data, "is_initialized"
    ), "ee.data.is_initialized is gone; initialize_ee()'s guard needs updating"
    assert callable(ee.data.is_initialized)


def test_initialisation_guard_returns_a_bool_without_credentials():
    # Safe to call uninitialised: it reports state, it does not create any.
    assert ee.data.is_initialized() in (True, False)


@pytest.mark.parametrize("name", ["Initialize", "Authenticate"])
def test_initialisation_entry_points_exist(name):
    assert callable(getattr(ee, name))


@pytest.mark.parametrize(
    "name",
    [
        "Image",
        "ImageCollection",
        "Date",
        "Number",
        "Algorithms",
        "Geometry",
    ],
)
def test_constructors_the_library_calls_exist(name):
    assert hasattr(ee, name), f"ee.{name} is gone; the library calls it"


# Not checked here: ee.Algorithms.If, used by broadband_emiss. Members of
# ee.Algorithms are resolved lazily against the initialized session's algorithm
# list, so touching one uninitialised raises AttributeError. Verifying it would
# need credentials, which is validation/'s job, not this suite's.


def test_image_constant_exists():
    # landsat_lst.add_timestamp builds the TIMESTAMP band with it.
    assert callable(ee.Image.constant)


def test_the_stale_private_guard_is_really_gone():
    # Pins the reason for the change: if a future earthengine-api reinstates
    # ee.data._initialized, this fails and someone can reconsider deliberately
    # rather than discovering it by accident.
    assert not hasattr(ee.data, "_initialized")

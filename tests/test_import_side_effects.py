"""Importing ee_lst must not change the caller's environment.

ee_lst/landsat_lst.py used to run this at import time:

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../.gee-sa-priv-key.json"

which silently overwrote whatever credentials the caller had configured, with
a *relative* path that resolved differently depending on the working directory.
Merely importing the library broke Application Default Credentials.

Import-time side effects cannot be observed from inside a process that has
already imported the module, so these tests spawn a clean interpreter.
"""

import pathlib
import subprocess
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
CREDS = "GOOGLE_APPLICATION_CREDENTIALS"
MODULES = [
    "ee_lst.landsat_lst",
    "ee_lst.aster_bare_emiss",
    "ee_lst.broadband_emiss",
    "ee_lst.cloudmask",
    "ee_lst.compute_emissivity",
    "ee_lst.compute_fvc",
    "ee_lst.compute_ndvi",
    "ee_lst.constants",
    "ee_lst.ncep_tpw",
    "ee_lst.smw_algorithm",
]


def run_child(code, env_extra=None):
    """Run `code` in a fresh interpreter rooted at the repo, return stdout."""
    import os

    env = dict(os.environ)
    env.pop(CREDS, None)
    env["PYTHONPATH"] = str(REPO_ROOT)
    if env_extra:
        env.update(env_extra)
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


@pytest.mark.parametrize("module", MODULES)
def test_import_does_not_set_credentials_when_caller_has_none(module):
    out = run_child(
        f"import os; import {module}; " f"print(os.environ.get({CREDS!r}, '<unset>'))"
    )
    assert out == "<unset>", f"importing {module} set {CREDS} to {out!r}"


@pytest.mark.parametrize("module", MODULES)
def test_import_does_not_overwrite_credentials_the_caller_set(module):
    sentinel = "/caller/chosen/service-account.json"
    out = run_child(
        f"import os; import {module}; print(os.environ[{CREDS!r}])",
        env_extra={CREDS: sentinel},
    )
    assert out == sentinel, f"importing {module} clobbered {CREDS}"


def test_no_module_writes_to_os_environ_at_all():
    # Belt and braces: catch a reintroduction under a different variable name.
    out = run_child(
        "import os; before = dict(os.environ); "
        "import ee_lst.landsat_lst; "
        "changed = {k: (before.get(k), v) for k, v in os.environ.items() "
        "          if before.get(k) != v}; "
        "print(changed)"
    )
    assert out == "{}", f"import mutated the environment: {out}"


def test_importing_the_package_does_not_initialise_earth_engine():
    # A network call at import time would make the library unusable offline
    # and would fail in CI, which has no credentials.
    out = run_child(
        "import ee_lst.landsat_lst; import ee; print(ee.data.is_initialized())"
    )
    assert out == "False"

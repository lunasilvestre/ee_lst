# Tests

Unit tests for `ee_lst`. They run in under a second, need **no Earth Engine
credentials and no network access**, and are wired into CI.

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest tests/ -v
```

## How these tests work

Earth Engine objects are lazy graph builders. `image.select("SR_B5").multiply(0.0000275)`
sends nothing anywhere — it describes work for the server to do later. Nothing is
computed until you ask for a result.

That property is what makes this library testable offline. The parts that
actually regress under refactoring are *structural*:

- which band gets selected for which satellite,
- which scale factor and offset get applied,
- which coefficient table gets indexed,
- what the output band is named.

All of that is visible in the call graph. So each test passes a
`unittest.mock.MagicMock` where an `ee.Image` would go, calls the function, and
asserts on the calls that were made. Modules that `import ee` directly get `ee`
patched per-test via pytest-mock's `mocker` fixture.

The tests therefore verify **wiring, not pixels**. They will catch a swapped
band, a dropped scale factor, a renamed output or a mangled coefficient table.
They will not tell you whether the retrieved temperature is correct — that is
what `validation/` is for, comparing GeoTIFF output against the original
JavaScript implementation.

### Helpers

`conftest.py` provides the `image` fixture plus a few call-graph helpers
(`selected_bands`, `renamed_bands`, `expressions`, `numeric_args`,
`calls_to`). They match on the *final* method name in a chain, so
`image.expression().where().where().rename("FVC")` is found the same as a bare
`image.rename("FVC")`. Without that, assertions would encode the exact chain
shape and break on any harmless refactor.

## Layout

```
tests/
├── conftest.py                  # image fixture + call-graph helpers
├── test_constants.py            # LANDSAT_BANDS and SMW_COEFFICIENTS, pinned to published values
├── test_aster_bare_emiss.py     # bare-ground emissivity from ASTER GED
├── test_broadband_emiss.py      # broad-band emissivity, five-band convolution
├── test_cloudmask.py            # QA_PIXEL bit masking, SR vs TOA
├── test_compute_emissivity.py   # per-satellite convolution coefficients, water/snow
├── test_compute_fvc.py          # fraction of vegetation cover
├── test_compute_ndvi.py         # NDVI, including the L8/L9 band-numbering branch
├── test_landsat_lst.py          # fetch_landsat_collection, the public entry point
├── test_ncep_tpw.py             # precipitable water interpolation and binning
└── test_smw_algorithm.py        # the Statistical Mono-Window retrieval
```

## What is deliberately pinned

`test_constants.py` asserts coefficients against literal values rather than
deriving them from the module under test. This library's value is that it
reproduces Ermida et al. (2020); if a coefficient moves, the port is wrong even
when every other test passes.

Two known source quirks are pinned as *current behaviour* rather than fixed,
because changing them would be a behavioural change:

- `smw_algorithm.add_lst_band` documents an L9 fallback for an unknown
  satellite, but reads `LANDSAT_BANDS[landsat]` with a direct index a few lines
  later, so the fallback is unreachable and a `KeyError` is raised first. In
  practice `fetch_landsat_collection` validates the satellite up front, so
  callers using the public entry point never reach it.
- `compute_emissivity.add_emissivity_band` has no L9 row in its convolution
  table and falls through to the L8 coefficients.

If either is ever changed deliberately, the corresponding test should be updated
in the same commit.

## Adding a test

Ask what could silently break without anything raising. A band name, a
threshold, a coefficient, a branch on satellite ID — those are worth a test. The
shape of a call chain is not; assert on the values, not the plumbing.

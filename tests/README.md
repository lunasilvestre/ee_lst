# Tests Folder README

The `tests` folder contains unit test scripts for various modules of the `ee_lst` project. These test scripts are based on the structure of the modules they're testing and serve as a starting point for comprehensive testing. Currently, the tests utilize mock data and placeholder functions.

## Structure

```
tests/
│
├── test_aster_bare_emiss.py # Tests for the ASTER bare emissivity calculations
├── test_broadband_emiss.py # Tests for broadband emissivity calculations
├── test_cloudmask.py # Tests for cloud masking functionality
├── test_compute_emissivity.py # Tests for emissivity computations
├── test_compute_fvc.py # Tests for fraction of vegetation cover (FVC) computations
├── test_compute_ndvi.py # Tests for NDVI computations
├── test_landsat_lst.py # Tests for Landsat LST computations
├── test_ncep_tpw.py # Tests for NCEP total precipitable water (TPW) calculations
└── test_smw_algorithm.py # Tests for split-window algorithm calculations
```


## Mock Testing

Currently, the tests utilize mock data and placeholder functions, meaning they don't use real datasets or expected outputs. Instead, they serve as scaffolds to be expanded upon. 

For example, in `test_landsat_lst.py`, the function `load_test_image` is a mock function meant to simulate loading an image. This, and other placeholder functions, should be replaced with actual logic as the project evolves.

To make these tests functional:

1. Replace mock data loading functions with actual data loading methods.
2. Replace placeholder expected output functions with actual expected output data.
3. Adjust assertion statements to compare actual outputs with expected outcomes.

## Running Tests

Though not fully functional, you can typically run the tests using a test runner like `pytest`. However, remember that the current tests will need more concrete data and logic to produce meaningful results.

```bash
pytest tests/
```

It's recommended to continually expand and refine these tests as the project grows to ensure that all functionality is thoroughly validated.
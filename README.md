# `ee_lst`

[![CI](https://github.com/lunasilvestre/ee_lst/actions/workflows/ci.yml/badge.svg)](https://github.com/lunasilvestre/ee_lst/actions/workflows/ci.yml) [![Refactoring Validation](https://github.com/lunasilvestre/ee_lst/actions/workflows/refactoring_validation.yml/badge.svg)](https://github.com/lunasilvestre/ee_lst/actions/workflows/refactoring_validation.yml)

Tested on Python 3.12 and 3.13.

`ee_lst` is a Python package designed to provide functionalities related to Land Surface Temperature (LST) computation using the Landsat series of satellites. This package expands the use of the original Google Earth Engine (GEE) code, initially crafted in JavaScript by [Sofia Ermida](https://github.com/sofiaermida). Transitioning to Python not only grants more versatility to the code but also broadens its accessibility. The original repository by Sofia Ermida can be accessed [here](https://github.com/sofiaermida/Landsat_SMW_LST).

## Table of Contents

- [Installation](#installation)
- [Authentication](#authentication)
- [Usage](#usage)
- [Refactoring Validation](#refactoring-validation)
- [Examples](#examples)
- [Documentation](#documentation)
- [Workflows](#workflows)
- [Testing](#testing)
- [Reference](#reference)
- [Contributing](#contributing)
- [License](#license)

## Installation

Requires Python 3.12 or 3.13.

```bash
git clone https://github.com/lunasilvestre/ee_lst.git
cd ee_lst

# The library. This is all you need to use ee_lst.
pip install .
```

`ee_lst` itself depends only on `earthengine-api`, which brings the Google client
stack with it.

Two further requirement files cover things the library itself does not need:

```bash
# Adds what the examples and the validation harness use:
# numpy, rasterio, folium
pip install -r requirements.txt

# Adds the linters and test runner, pinned to the versions CI uses
pip install -r requirements-dev.txt
```

## Authentication

`ee_lst` does not configure credentials for you, and importing it does not touch
your environment. Authenticate with Earth Engine however you normally would,
before calling into the library:

```bash
# Interactive, once per machine
earthengine authenticate
```

```bash
# Or point Application Default Credentials at a service account key
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your-key.json
```

You can also call `ee.Initialize()` yourself with your own credentials first —
`fetch_landsat_collection` will use the already-initialized session.

Either way the account must be **registered with an Earth Engine project**.
Credentials alone are not enough; without registration Earth Engine returns
`Not signed up for Earth Engine or project is not registered`.

## Usage

```python
import ee
from ee_lst.landsat_lst import fetch_landsat_collection

geometry = ee.Geometry.Rectangle([-8.91, 40.0, -8.3, 40.4])

collection = fetch_landsat_collection(
    "L8",              # one of L4, L5, L7, L8, L9
    "2022-05-15",      # start date
    "2022-05-31",      # end date
    geometry,
    True,              # use_ndvi: dynamic emissivity from NDVI
)

image = collection.first()
lst = image.select("LST")   # land surface temperature, kelvin
```

Each image in the returned collection carries the added bands `NDVI`, `FVC`,
`TPW`, `TPWpos`, `EM`, `LST` and `TIMESTAMP` alongside the source bands.

For running this package under Docker, particularly around credential handling,
see [this guide](./.github/workflows/README.md).


## Refactoring Validation

Ensuring consistent outputs between the original JavaScript version and the refactored Python library is of paramount importance. We've established a validation process housed within the `validation` directory to ensure consistency. This process, largely automated by the `refactoring_validation.yml` workflow, involves:

- Adapting the original JavaScript library for NodeJS execution.
- Containerizing both the adapted JavaScript and refactored Python libraries using Docker.
- Generating GeoTIFF outputs from both libraries.
- Comparing these outputs for discrepancies.

More details about this validation process, including its structure and exact steps, can be found in the [validation README](./validation/README.md).

## Examples

Locate examples in the examples directory. To execute one:

```
python examples/example_1.py
```

More examples will be available soon.

## Documentation

Documentation is housed in the docs directory. Also find a copy of [Ermida *et al*. (2020)](https://doi.org/10.3390/rs12091471) there.


## Workflows
For insights into our CI/CD procedures and other workflows, peruse the [workflows directory](./.github/workflows/README.md).

## Testing

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest tests/
```

The suite mocks the Earth Engine client, so it runs in about a second and needs
**no credentials and no network access**. It checks the things that regress
silently under refactoring — per-satellite band selection, scale factors,
coefficient tables, output band names — rather than pixel values. Verifying the
numbers is the [validation harness](./validation/README.md)'s job.

For a deeper dive, see the [tests README](./tests/README.md).

## Reference

If leveraging this code or its derivative data, kindly cite:

Ermida, S.L., Soares, P., Mantas, V., Göttsche, F.-M., Trigo, I.F., 2020. 
    Google Earth Engine open-source code for Land Surface Temperature estimation from the Landsat series.
    Remote Sensing, 12 (9), 1471; [https://doi.org/10.3390/rs12091471](https://doi.org/10.3390/rs12091471)

## Contributing

Contributions are welcome! Please read the contributing guidelines (if available) before making any changes.

## License

For licensing details, view the [LICENSE](./LICENSE) file.

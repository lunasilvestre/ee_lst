# `ee_lst`

![CI/CD Workflow](https://github.com/lunasilvestre/ee_lst/actions/workflows/ci.yml/badge.svg)

`ee_lst` is a Python package designed to provide functionalities related to Land Surface Temperature (LST) computation using the Landsat series of satellites. This package expands the use of the original Google Earth Engine (GEE) code, initially crafted in JavaScript by [Sofia Ermida](https://github.com/sofiaermida). Transitioning to Python not only grants more versatility to the code but also broadens its accessibility. The original repository by Sofia Ermida can be accessed [here](https://github.com/sofiaermida/Landsat_SMW_LST).

## Table of Contents

- [Installation](#installation)
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

To install the `ee_lst` package, follow these steps:

```
# Clone the repository
git clone https://github.com/lunasilvestre/ee_lst.git

# Navigate to the repository directory
cd ee_lst

# Install the package and its dependencies
pip install . && pip install -r requirements.txt
```


## Usage

For using this package with Docker, especially regarding handling credentials, see [this guide](./.github/workflows/README.md).


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

Tests reside in the tests directory. To initiate them:

```
pytest tests/
```

For a deeper dive into testing, check out the [tests README](./tests/README.md)

## Reference

If leveraging this code or its derivative data, kindly cite:

Ermida, S.L., Soares, P., Mantas, V., Göttsche, F.-M., Trigo, I.F., 2020. 
    Google Earth Engine open-source code for Land Surface Temperature estimation from the Landsat series.
    Remote Sensing, 12 (9), 1471; [https://doi.org/10.3390/rs12091471](https://doi.org/10.3390/rs12091471)

## Contributing

Contributions are welcome! Please read the contributing guidelines (if available) before making any changes.

## License

For licensing details, view the [LICENSE](./LICENSE) file.

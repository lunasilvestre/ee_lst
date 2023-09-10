# `ee_lst`

`ee_lst` is a Python package designed to provide functionalities related to Land Surface Temperature (LST) computation using the Landsat series of satellites. This repository contains the source code, examples, and documentation for the package.

This package is designed to expand the use of the original Google Earth Engine (GEE) code for Land Surface Temperature (LST) computation using the Landsat series of satellites. While the original code by [Sofia Ermida](https://github.com/sofiaermida) was implemented in JavaScript for the GEE environment, which primarily runs in the browser, this library brings the implementation to Python. This transition not only makes the code more versatile but also increases its reach to a broader audience familiar with Python. This repository contains the source code, examples, and documentation for the package. The original repository by Sofia Ermida can be found [here](https://github.com/sofiaermida/Landsat_SMW_LST).

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
  - [Examples](#examples)
- [Documentation](#documentation)
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

# Install the package
pip install .
```

Ensure you have the required dependencies by installing them from the \`requirements.txt\`:

```
pip install -r requirements.txt
```

## Usage

### Examples

Several examples are provided in the \`examples\` directory:

- [example_1.py](./examples/example_1.py)
- [example_2.js](./examples/example_2.js)
- [example_gee_book.py](./examples/example_gee_book.py)

To run a functioning example:

```
python examples/example_1.py
```

(Other examples will be published shortly.)

## Documentation

The documentation for the `ee_lst` package can be found in the `docs` directory. A copy of Sofia Ermida's [paper](https://doi.org/10.3390/rs12091471) (see **Reference** below) is also made available in the `docs` folder.

## Testing

Tests for the package functionalities are located in the `tests` directory. To run the tests:

```
# Navigate to the tests directory
cd tests

# Run the tests
python -m unittest discover
```

## Reference

This repository is derived from the work by Sofia Ermida on Google Earth Engine code to compute Land Surface Temperature from the Landsat series of satellites. If you use this code or any data derived from it, please cite the following reference:

Ermida, S.L., Soares, P., Mantas, V., Göttsche, F.-M., Trigo, I.F., 2020. 
    Google Earth Engine open-source code for Land Surface Temperature estimation from the Landsat series.
    Remote Sensing, 12 (9), 1471; [https://doi.org/10.3390/rs12091471](https://doi.org/10.3390/rs12091471)

## Contributing

Contributions are welcome! Please read the contributing guidelines (if available) before making any changes.

## License

This project is licensed under the terms of the [LICENSE](./LICENSE) file.

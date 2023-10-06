# Refactoring Validation

This directory (`validation`) is dedicated to tools and resources required for the validation of the refactoring process. The goal is to ensure the refactored Python library provides consistent results with the original library, designed in JavaScript for the Google Earth Engine editor. The script `modify_files.sh` adapts this original library for execution in a NodeJS environment, enabling headless testing.

## Directory Structure

- [`Dockerfile.ee_lst`](./Dockerfile.ee_lst): Dockerfile for the refactored Python library.
- [`Dockerfile.landsat_lst`](./Dockerfile.landsat_lst): Dockerfile for the NodeJS-adapted original JavaScript library.
- [`example_1_node.js`](./example_1_node.js): A NodeJS-enabled version of the original `example_1.js`.
- [`example_1_service_account.py`](./example_1_service_account.py): A Python version of the original `example_1.js` that runs headlessly using a service account.
- [`modify_files.sh`](./modify_files.sh): Script to adapt the original JavaScript library for headless execution in NodeJS.
- [`geotiffs_comparison.py`](./geotiffs_comparison.py): Script for comparing generated GeoTIFFs.

## Validation Process

1. **Setup**:
   - Dockerfiles containerize both the NodeJS-adapted original JavaScript library and the refactored Python library.
   - The `modify_files.sh` script modifies the original library for headless execution in NodeJS.
   
2. **Generate Outputs**:
   - Both libraries produce GeoTIFF images (through specific commands or functions).
   - Images are saved in separate directories, typically named `nodejs_downloads` and `python_downloads`.
   
3. **Image Comparison**:
   - Run `geotiffs_comparison.py` to compare the images.
   - This script evaluates size and pixel value differences.
   - Detailed differences are saved and a summary is printed.
   
4. **Criteria for Validation**:
   - A size difference threshold (e.g., 0.5%) is set.
   - Pixel value differences should be minimal or within acceptable bounds.
   
5. **Integration with CI/CD**:
   - The GitHub workflow `refactoring_validation.yml` automates this validation.
   - It manages Docker containers, generates outputs, and runs the comparison.
   - Workflow failures indicate discrepancies in refactoring.

## Note
The validation process ensures library integrity during and after refactoring. It's crucial to maintain and expand these validation tools as the library evolves.

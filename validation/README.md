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
   - It evaluates size and pixel value differences, printing a summary per band.

4. **Criteria for Validation**:
   - **Pixel values must match exactly.** Mean, max and min difference must all be
     `0`. There is no numerical tolerance and there should not be one — both
     implementations send the same graph to the same Earth Engine servers, so any
     nonzero delta means the port has diverged.
   - Image *size* has a 0.5% tolerance, since the two clients can request very
     slightly different windows.
   - Every band must be present on **both** sides. A band exported by only one
     implementation is a band nobody checked.

5. **Integration with CI/CD**:
   - The GitHub workflow `refactoring_validation.yml` automates this validation.
   - It manages Docker containers, generates outputs, and runs the comparison.
   - Triggers: every push to `main`, monthly on the 1st, and `workflow_dispatch`
     for on-demand runs.
   - Workflow failures indicate discrepancies in refactoring.

## How the comparison can fail

`geotiffs_comparison.py` exits non-zero, and says which of these applies, when:

- a download directory is missing — the container never ran;
- **nothing was compared** — the directories exist but hold no matching pair.
  This used to exit `0`: the script looped over an empty directory, did nothing,
  and reported success. A validation job that cannot fail is worse than none;
- the two sides disagree about which bands exist, in *either* direction;
- any band differs by any amount.

The both-directions check is not hypothetical. A real run had the JavaScript
container export 3 of 8 bands while Python exported all 8; because the unmatched
files were the extra ones, a one-directional check saw nothing wrong and the job
passed having validated well under half the output.

## Reproducibility

`Dockerfile.landsat_lst` pins the upstream clone to
`65fd1ae9c752b6e3f738405495bcb1b5c773cf4d` ("Update to process Landsat9",
2023-08-02) and asserts the SHA after checkout. Upstream is archived, and
`modify_files.sh` sed-edits a hardcoded list of module filenames, so an
unpinned clone would let a reorganisation upstream break the harness silently.

`modify_files.sh` rewrites 8 of the 10 upstream modules. That is correct, not an
omission: `cloudmask.js` and `compute_FVC.js` mention the Code Editor require
path only inside their header comments and contain no real `require()` calls.

## Credentials

The service account key is mounted at run time with `-v`; no Dockerfile `COPY`s
it and it is absent from every image layer. The repo's `.dockerignore` also keeps
it out of the build context entirely — the workflow writes
`.gee-sa-priv-key.json` into the repo root *before* building, and the build
context is the repo root.

## Note
The validation process ensures library integrity during and after refactoring. It's crucial to maintain and expand these validation tools as the library evolves.

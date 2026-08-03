# GitHub Workflows Guide

This guide provides instructions for setting up continuous integration (CI) and refactoring validation workflows for the project. It also outlines best practices for handling sensitive credentials when working with Docker.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Building Docker Containers Locally](#building-docker-containers-locally)
  - [Avoid Embedding Credentials](#avoid-embedding-credentials)
  - [Keeping the key out of the build context too](#keeping-the-key-out-of-the-build-context-too)
- [GitHub Workflows](#github-workflows)
  - [Continuous Integration (CI)](#continuous-integration-ci)
  - [Refactoring Validation](#refactoring-validation)

## Prerequisites

- Ensure you have Docker installed on your local machine.
- Ensure you have a Google Cloud Platform (GCP) service account key saved as `.gee-sa-priv-key.json`.
- The service account must be **registered with an Earth Engine project**. A valid
  key is not sufficient on its own — without registration Earth Engine returns
  `Not signed up for Earth Engine or project is not registered`.

## Building Docker Containers Locally

Both images are built from the **repository root**, not from this directory:

```bash
docker build -f validation/Dockerfile.ee_lst      -t python_lst .
docker build -f validation/Dockerfile.landsat_lst -t node_lst   .
```

`Dockerfile.ee_lst` runs the refactored Python library (`python:3.13-slim`).
`Dockerfile.landsat_lst` runs the original JavaScript under NodeJS (`node:20`),
cloning upstream at a pinned commit.

### Avoid Embedding Credentials

For security reasons, avoid embedding Google Earth Engine service account credentials in the Docker image. Instead, mount the credentials file from your local machine into the Docker container at runtime. This ensures that the credentials stay on your local machine and aren't embedded into the image.

1. **Local Machine**:
   - Make sure the `.gee-sa-priv-key.json` file is saved on your local machine.

2. **Docker Run Command**:
   - Use the `docker run` command with the `-v` option to mount the credentials file into the container.

   ```bash
   docker run -v $(pwd)/.gee-sa-priv-key.json:/app/.gee-sa-priv-key.json my-image
   ```

In the above command:

- `-v $(pwd)/.gee-sa-priv-key.json:/app/.gee-sa-priv-key.json` mounts the `.gee-sa-priv-key.json` file from your current directory (`$(pwd)`) to `/app/.gee-sa-priv-key.json` inside the container.
- `my-image` is the name of your Docker image.

The application inside the Docker container can now access the `.gee-sa-priv-key.json` file at `/app/.gee-sa-priv-key.json`.

### Keeping the key out of the build context too

Mounting at run time keeps the key out of the image **layers**, but not out of the
**build context**. The context here is the repository root, and the validation
workflow writes `.gee-sa-priv-key.json` into that root *before* it builds either
image — so every build was handing the key to the Docker daemon even though no
`COPY` ever referenced it.

The repository's `.dockerignore` excludes it, along with `.git`, `.venv` and the
download directories. If you add a Dockerfile, keep it that way: check what the
daemon actually receives rather than assuming, for example with a throwaway image
that copies the context and lists it.

## GitHub Workflows

### Continuous Integration (CI)

The CI workflow (`ci.yml`) runs on every push and pull request. It needs no
credentials and makes no network calls beyond installing dependencies. Two jobs:

**`build`** — quality gate, on Python 3.13:

1. Checkout the code.
2. Set up Python (**pinned to 3.13**, deliberately not `3.x`: a floating version
   drifts onto a new release and turns a passing build red with no commit).
3. Cache Python dependencies to speed up future runs.
4. Install from `requirements.txt` and `requirements-dev.txt`.
5. Lint with `flake8`.
6. Check formatting with `black`.
7. **Run the test suite** with `pytest`.

**`install`** — packaging gate, matrixed over Python **3.12 and 3.13**:

1. Checkout the code.
2. Set up the matrix Python version.
3. `pip install .` into a clean venv.
4. Import `ee_lst.landsat_lst` from outside the source tree, asserting it resolves
   inside `site-packages` — importing from the repo root would pass even if the
   package were declared or built wrongly.
5. Assert the wheel ships no top-level `examples` module.

This second job exists because `build` installs `requirements.txt` and never
touches `setup.py`, so it cannot catch a broken `install_requires`. That is
exactly how an unbuildable dependency survived for years: `pip install -r
requirements.txt` worked while `pip install .` did not, and CI only ran the
former.

Linters and the test runner are pinned in `requirements-dev.txt` so local runs and
CI cannot drift. Note that `black` carries the `[jupyter]` extra — bare `black`
silently skips `.ipynb` files, which would leave the example notebook formatted
locally and unchecked in CI.

To view the complete CI configuration, refer to the [`ci.yml`](./ci.yml) file.

### Refactoring Validation

The Refactoring Validation workflow (`refactoring_validation.yml`) validates
refactoring by comparing the outputs of the original library and the current
library using Docker containers. It is the only workflow that needs credentials,
and the only one that proves the numbers are unchanged.

Triggers:

- every push to `main`;
- monthly, on the 1st (was weekly — the job burns Earth Engine quota and Drive
  I/O to re-prove something that only changes when the code does);
- `workflow_dispatch`, for on-demand runs.

Steps in the workflow include:

1. Checkout the code from the repository.
2. Set up GCP credentials from GitHub secrets.
3. Create directories for downloads.
4. Build and run the original library Docker container.
5. Build and run the current library Docker container.
6. Install necessary Python dependencies.
7. Compare the results using the provided comparison script.

**The comparison has no numerical tolerance.** Mean, max and min pixel difference
must all be exactly `0`; only image size has a tolerance, at 0.5%. Every band must
also be present on both sides — a band exported by only one implementation is a
band nobody checked. See the [validation README](../../validation/README.md) for
the failure modes and why they are strict.

To view the complete Refactoring Validation configuration, refer to the [`refactoring_validation.yml`](./refactoring_validation.yml) file.

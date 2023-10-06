# GitHub Workflows Guide

This guide provides instructions for setting up continuous integration (CI) and refactoring validation workflows for the project. It also outlines best practices for handling sensitive credentials when working with Docker.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Building Docker Containers Locally](#building-docker-containers-locally)
  - [Avoid Embedding Credentials](#avoid-embedding-credentials)
- [GitHub Workflows](#github-workflows)
  - [Continuous Integration (CI)](#continuous-integration-ci)
  - [Refactoring Validation](#refactoring-validation)

## Prerequisites

- Ensure you have Docker installed on your local machine.
- Ensure you have a Google Cloud Platform (GCP) service account key saved as `.gee-sa-priv-key.json`.

## Building Docker Containers Locally

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

## GitHub Workflows

### Continuous Integration (CI)

The CI workflow (`ci.yml`) ensures that the code quality meets the standards. It runs on every push and pull request.

Steps in the workflow include:

1. Checkout the code from the repository.
2. Set up the desired Python version.
3. Cache Python dependencies to speed up future runs.
4. Install project dependencies and linting tools.
5. Lint the code using `flake8`.
6. Check code formatting with `black`.

To view the complete CI configuration, refer to the [`ci.yml`](./ci.yml) file.

### Refactoring Validation

The Refactoring Validation workflow (`refactoring_validation.yml`) validates refactoring by comparing the outputs of the original library and the current library using Docker containers. This workflow runs on pushes to the `main` branch and is scheduled to run weekly.

Steps in the workflow include:

1. Checkout the code from the repository.
2. Set up GCP credentials from GitHub secrets.
3. Create directories for downloads.
4. Build and run the original library Docker container.
5. Build and run the current library Docker container.
6. Install necessary Python dependencies.
7. Compare the results using the provided comparison script.

To view the complete Refactoring Validation configuration, refer to the [`refactoring_validation.yml`](./refactoring_validation.yml) file.

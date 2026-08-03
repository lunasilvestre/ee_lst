from setuptools import setup, find_packages

# Was a backslash continuation, which baked 8 literal spaces into the middle of
# the published description ("...Surface        Temperature...").
DESCRIPTION = "Python library for Landsat Surface Temperature with Google Earth Engine"

setup(
    name="ee_lst",
    version="0.1.0",
    description=DESCRIPTION,
    author="Nelson Luna Silvestre",
    author_email="lunasilvestre@mailbox.org",
    url="https://github.com/lunasilvestre/ee_lst",
    # include= is load-bearing. A bare find_packages() also matches examples/,
    # which has an __init__.py, so `pip install ee_lst` would drop a top-level
    # `examples` package into site-packages.
    packages=find_packages(include=["ee_lst*"]),
    install_requires=[
        # ee_lst imports only `ee` (plus stdlib os). earthengine-api pulls the
        # rest of the stack transitively: google-api-python-client,
        # google-auth, google-auth-httplib2, google-cloud-storage, httplib2,
        # requests, cryptography.
        #
        # Deliberately NOT listed:
        #   numpy, rasterio - used only by validation/geotiffs_comparison.py
        #   folium          - used only by examples/example_1.py
        #   pyCrypto        - vestigial; nothing under ee/ or google/ imports
        #                     Crypto, and it cannot build on Python 3.11+
        # All of those live in requirements.txt instead.
        "earthengine-api",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)

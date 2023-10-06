from setuptools import setup, find_packages

setup(
    name="ee_lst",
    version="0.1.0",
    description="Python library for Landsat Surface\
        Temperature with Google Earth Engine",
    author="Nelson Luna Silvestre",
    author_email="lunasilvestre@mailbox.org",
    url="https://github.com/lunasilvestre/ee_lst",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "rasterio",
        "google-api-python-client",
        "pyCrypto",
        "earthengine-api"
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
    ],
)

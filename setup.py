"""
Setup configuration for VariantFlow-MMR
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read version from __version__.py
version_file = Path("src/vflow/__version__.py")
version_locals = {}
exec(version_file.read_text(), version_locals)
__version__ = version_locals["__version__"]

# Read long description from README (if exists)
long_description = ""
readme_file = Path("README.md")
if readme_file.exists():
    long_description = readme_file.read_text()

setup(
    name="variant-flow-mmr",
    version=__version__,
    author="Carla Rodrigues",
    author_email="Carlabio.biomol@gmail.com",
    description="Clinical-grade QC tool for Lynch Syndrome MMR genes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/carla-bioinfo/variant-flow-mmr",
    license="MIT",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.9",
    install_requires=[
        "pandas>=2.0.3",
        "numpy>=1.24.3",
        "biopython>=1.81",
        "pysam>=0.21.0",
        "typer>=0.9.0",
        "jinja2>=3.1.2",
        "requests>=2.31.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black>=23.7.0",
            "ruff>=0.0.292",
            "mypy>=1.5.0",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
)

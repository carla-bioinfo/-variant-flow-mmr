"""
VariantFlow-MMR: Clinical-grade QC for Lynch Syndrome

A professional tool for quality control and ACMG evidence collection
for mismatch repair (MMR) gene variants in Lynch Syndrome.
"""

__version__ = "0.1.0"
__author__ = "Carla Rodrigues"
__email__ = "Carlabio.biomol@gmail.com"

from . import core, cli, reports, validators

__all__ = ["core", "cli", "reports", "validators"]

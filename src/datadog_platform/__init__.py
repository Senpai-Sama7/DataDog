"""
DataDog Platform - Universal Data Orchestration Platform

A production-grade, horizontally scalable data orchestration platform.
"""

__version__ = "0.1.0"

from datadog_platform.core.pipeline import Pipeline
from datadog_platform.core.data_source import DataSource
from datadog_platform.core.transformation import Transformation
from datadog_platform.core.executor import Executor

__all__ = [
    "Pipeline",
    "DataSource",
    "Transformation",
    "Executor",
    "__version__",
]

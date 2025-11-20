"""Pytest configuration and shared fixtures for MATILDA tests.

This module configures pytest for the MATILDA test suite and provides
shared fixtures for all test modules.
"""

import pytest
import sys
from pathlib import Path

# Add fixtures to the path
fixtures_path = Path(__file__).parent / "fixtures"
sys.path.insert(0, str(fixtures_path))

# Import all fixtures from test_databases
from tests.fixtures.test_databases import (
    university_db,
    employee_db,
    retail_db,
    all_test_databases,
    TestDatabaseFactory
)

# Make fixtures available globally
__all__ = [
    'university_db',
    'employee_db', 
    'retail_db',
    'all_test_databases',
    'TestDatabaseFactory'
]

"""Pytest fixtures for Enterprise HR Agent tests."""

import pytest
import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.integrations.mock_saas_server import mock_backend
from src.storage.database import init_db

@pytest.fixture(autouse=True)
def setup_teardown():
    mock_backend.reset_data()
    init_db()
    yield
    mock_backend.reset_data()

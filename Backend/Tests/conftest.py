import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture(scope="session")
def test_client():
    """Simule un client API de secours."""
    from unittest.mock import MagicMock
    mock_client = MagicMock()
    mock_client.post.return_value.status_code = 200
    mock_client.post.return_value.json.return_value = {"status": "success"}
    return mock_client

@pytest.fixture(scope="function")
def mock_db():
    """Mock la base de données."""
    from unittest.mock import MagicMock
    return MagicMock()

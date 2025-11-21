"""
Pytest configuration and shared fixtures for DevPulse tests.

Provides common test fixtures, mock data, and setup/teardown logic.
"""

import pytest
import tempfile
import shutil
from typing import Generator
from fastapi.testclient import TestClient
from backend.main import app
from backend.config import reload_settings


@pytest.fixture
def test_client() -> TestClient:
    """Provide FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """Provide temporary directory that is cleaned up after test."""
    tmpdir = tempfile.mkdtemp()
    yield tmpdir
    shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.fixture
def mock_radon_output() -> str:
    """Provide mock radon cc output."""
    return """backend/services/analyzer.py
    M 45:4 AnalyzerClass.analyze_method - B (6)
    F 12:0 simple_function - A (3)
backend/utils/parser.py
    F 20:0 parse_data - C (8)
    F 35:0 validate_input - A (2)
"""


@pytest.fixture
def mock_cloc_output() -> str:
    """Provide mock CLOC JSON output."""
    return """{
  "header": {
    "cloc_version": "1.90",
    "n_files": 10
  },
  "Python": {
    "nFiles": 10,
    "blank": 150,
    "comment": 200,
    "code": 1000
  },
  "SUM": {
    "blank": 150,
    "comment": 200,
    "code": 1000
  }
}"""


@pytest.fixture
def mock_pylint_output() -> str:
    """Provide mock pylint output."""
    return """************* Module backend.services.analyzer
backend/services/analyzer.py:45:0: C0103: Variable name 'x' doesn't conform to snake_case
backend/services/analyzer.py:67:0: W0612: Unused variable 'temp'
backend/services/analyzer.py:89:0: E1101: Instance of 'dict' has no 'get' member

-----------------------------------
Your code has been rated at 7.50/10
"""


@pytest.fixture
def mock_analysis_result() -> dict:
    """Provide mock complete analysis result."""
    return {
        "repo_url": "https://github.com/test/repo",
        "git_sha": "abc123def456",
        "radon": {
            "average_complexity": 4.75,
            "total_functions": 4,
            "blocks": [
                {
                    "name": "analyze_method",
                    "complexity": 6,
                    "grade": "B",
                    "type": "method",
                    "file": "backend/services/analyzer.py",
                    "location": "45:4"
                }
            ],
            "total_complexity": 19
        },
        "cloc": {
            "code": 1000,
            "comment": 200,
            "blank": 150,
            "languages": {
                "Python": {
                    "code": 1000,
                    "comment": 200,
                    "blank": 150,
                    "files": 10
                }
            },
            "total_files": 10
        },
        "pylint": {
            "score": 7.5,
            "issues": [],
            "issue_counts": {
                "error": 1,
                "warning": 1,
                "convention": 1,
                "refactor": 0
            },
            "total_issues": 3
        },
        "ai_metrics": {
            "ai_probability": 0.3,
            "ai_risk_notes": "Moderate AI code probability detected",
            "recommendations": [
                "Review complex functions",
                "Add more tests",
                "Improve documentation"
            ]
        },
        "code_health_score": 65.5,
        "historical_risk_score": 0.35
    }


@pytest.fixture(autouse=True)
def reset_settings():
    """Reset settings before each test."""
    reload_settings()
    yield
    reload_settings()

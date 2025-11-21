"""
Unit tests for parser modules.

Tests radon, pylint, and CLOC parsers with various input scenarios.
"""

import pytest
from backend.utils.radon_parser import parse_radon_output
from backend.utils.pylint_parser import parse_pylint_output
from backend.utils.cloc_parser import parse_cloc_output


class TestRadonParser:
    """Tests for radon output parser."""
    
    def test_parse_valid_output(self, mock_radon_output):
        """Test parsing valid radon output."""
        result = parse_radon_output(mock_radon_output)
        
        assert result["total_functions"] == 4
        assert result["average_complexity"] > 0
        assert len(result["blocks"]) == 4
        assert result["total_complexity"] == 19
    
    def test_parse_empty_output(self):
        """Test parsing empty output."""
        result = parse_radon_output("")
        
        assert result["total_functions"] == 0
        assert result["average_complexity"] == 0
        assert result["blocks"] == []
    
    def test_parse_error_output(self):
        """Test parsing output with errors."""
        result = parse_radon_output("Error: command failed")
        
        assert result["total_functions"] == 0
        assert result["average_complexity"] == 0
    
    def test_parse_malformed_output(self):
        """Test parsing malformed output."""
        malformed = "some random text\nwithout proper format"
        result = parse_radon_output(malformed)
        
        # Should not crash, returns empty result
        assert isinstance(result, dict)
        assert "total_functions" in result


class TestPylintParser:
    """Tests for pylint output parser."""
    
    def test_parse_valid_output(self, mock_pylint_output):
        """Test parsing valid pylint output."""
        result = parse_pylint_output(mock_pylint_output)
        
        assert result["score"] == 7.5
        assert result["total_issues"] == 3
        assert result["issue_counts"]["error"] == 1
        assert result["issue_counts"]["warning"] == 1
        assert result["issue_counts"]["convention"] == 1
    
    def test_parse_empty_output(self):
        """Test parsing empty output."""
        result = parse_pylint_output("")
        
        assert result["score"] == 5.0
        assert result["total_issues"] == 0
    
    def test_parse_perfect_score(self):
        """Test parsing output with perfect score."""
        output = "Your code has been rated at 10.00/10"
        result = parse_pylint_output(output)
        
        assert result["score"] == 10.0
    
    def test_parse_negative_score(self):
        """Test parsing output with negative score."""
        output = "Your code has been rated at -2.50/10"
        result = parse_pylint_output(output)
        
        assert result["score"] == -2.5
    
    def test_issue_categorization(self):
        """Test that issues are properly categorized by severity."""
        output = """
backend/test.py:1:0: E0001: Syntax error
backend/test.py:2:0: W0612: Unused variable
backend/test.py:3:0: C0103: Invalid name
backend/test.py:4:0: R0903: Too few public methods

Your code has been rated at 5.00/10
"""
        result = parse_pylint_output(output)
        
        assert result["issue_counts"]["error"] == 1
        assert result["issue_counts"]["warning"] == 1
        assert result["issue_counts"]["convention"] == 1
        assert result["issue_counts"]["refactor"] == 1


class TestClocParser:
    """Tests for CLOC output parser."""
    
    def test_parse_json_output(self, mock_cloc_output):
        """Test parsing JSON CLOC output."""
        result = parse_cloc_output(mock_cloc_output)
        
        assert result["code"] == 1000
        assert result["comment"] == 200
        assert result["blank"] == 150
        assert result["total_files"] == 10
        assert "Python" in result["languages"]
    
    def test_parse_empty_output(self):
        """Test parsing empty output."""
        result = parse_cloc_output("")
        
        assert result["code"] == 0
        assert result["total_files"] == 0
    
    def test_parse_invalid_json(self):
        """Test parsing invalid JSON."""
        result = parse_cloc_output("{invalid json")
        
        # Should fallback to radon parser or return empty
        assert isinstance(result, dict)
        assert "code" in result
    
    def test_parse_multiple_languages(self):
        """Test parsing output with multiple languages."""
        output = """{
  "header": {"n_files": 20},
  "Python": {"nFiles": 10, "code": 1000, "comment": 100, "blank": 50},
  "JavaScript": {"nFiles": 10, "code": 500, "comment": 50, "blank": 25},
  "SUM": {"code": 1500, "comment": 150, "blank": 75}
}"""
        result = parse_cloc_output(output)
        
        assert result["code"] == 1500
        assert result["total_files"] == 20
        assert len(result["languages"]) == 2
        assert "Python" in result["languages"]
        assert "JavaScript" in result["languages"]

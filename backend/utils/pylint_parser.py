"""
Pylint output parser for code quality analysis.

Parses output from 'pylint' command with comprehensive error handling,
issue categorization, and severity levels.
"""

import re
from typing import Dict, Any, List
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)


def parse_pylint_output(output: str) -> Dict[str, Any]:
    """
    Parse pylint output with comprehensive error handling.
    
    Args:
        output: Raw pylint output
    
    Returns:
        Dictionary containing:
            - score: Code quality score (0-10)
            - issues: List of parsed issues with severity
            - issue_counts: Count by severity level
    """
    if not output:
        logger.warning("Pylint output is empty")
        return _empty_pylint_result()
    
    
    try:
        lines = [l for l in output.splitlines() if l.strip()]
        score = None
        issues: List[Dict[str, Any]] = []
        issue_counts = {"error": 0, "warning": 0, "convention": 0, "refactor": 0}
        
        for line in lines:
            # Look for the rating line
            if "Your code has been rated at" in line:
                score = _extract_score(line)
                logger.debug(f"Extracted pylint score: {score}")
            
            # Parse issue lines
            elif line.strip() and not line.startswith("---"):
                issue = _parse_issue_line(line)
                if issue:
                    issues.append(issue)
                    severity = issue.get('severity', 'warning')
                    if severity in issue_counts:
                        issue_counts[severity] += 1
        
        # If no score found, default to 5.0
        if score is None:
            score = 5.0
            logger.warning("No pylint score found in output, defaulting to 5.0")
        
        result = {
            "score": score,
            "issues": issues[:50],  # Limit to 50 most important issues
            "issue_counts": issue_counts,
            "total_issues": len(issues)
        }
        
        logger.info(
            f"Pylint parsing complete: score={score}, "
            f"total_issues={len(issues)}, "
            f"errors={issue_counts['error']}, "
            f"warnings={issue_counts['warning']}"
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Pylint parsing error: {e}", exc_info=True)
        return _empty_pylint_result()


def _extract_score(line: str) -> float:
    """
    Extract score from pylint rating line.
    
    Args:
        line: Line containing "Your code has been rated at X/10"
    
    Returns:
        Extracted score or 5.0 if extraction fails
    """
    try:
        match = re.search(r"rated at\s+([-+]?\d+\.?\d*)/10", line)
        if match:
            return float(match.group(1))
    except Exception as e:
        logger.warning(f"Failed to extract score from line: {line} - {e}")
    return 5.0


def _parse_issue_line(line: str) -> Dict[str, Any]:
    """
    Parse a single pylint issue line.
    
    Format: "path/file.py:123:4: C0103: Variable name 'x' doesn't conform to snake_case"
    
    Args:
        line: Issue line to parse
    
    Returns:
        Dictionary with issue details or None if parsing fails
    """
    try:
        # Pattern: file:line:col: CODE: message
        pattern = r'^(.+?):(\d+):(\d+):\s*([CRWEF]\d+):\s*(.+)$'
        match = re.match(pattern, line)
        
        if match:
            file_path, line_num, col, code, message = match.groups()
            
            # Determine severity from code prefix
            severity_map = {
                'C': 'convention',
                'R': 'refactor',
                'W': 'warning',
                'E': 'error',
                'F': 'error'
            }
            severity = severity_map.get(code[0], 'warning')
            
            return {
                "file": file_path.strip(),
                "line": int(line_num),
                "column": int(col),
                "code": code,
                "message": message.strip(),
                "severity": severity
            }
    except Exception as e:
        logger.debug(f"Failed to parse issue line: {line[:100]} - {e}")
    
    return None


def _empty_pylint_result() -> Dict[str, Any]:
    """Return empty pylint result structure."""
    return {
        "score": 5.0,
        "issues": [],
        "issue_counts": {"error": 0, "warning": 0, "convention": 0, "refactor": 0},
        "total_issues": 0
    }
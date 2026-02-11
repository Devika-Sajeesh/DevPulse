"""
Radon output parser for cyclomatic complexity analysis.

Parses output from 'radon cc' command with comprehensive error handling
and validation.
"""

from typing import Dict, Any, List
import re
from backend.utils.logger import setup_logger
from backend.utils.exceptions import AnalysisError

logger = setup_logger(__name__)


def parse_radon_output(radon_output: str) -> Dict[str, Any]:
    """
    Parse radon cc output correctly.
    
    Expected format:
        path/to/file.py
            M 45:4 ClassName.method_name - B (6)
            F 12:0 function_name - A (3)
    
    Args:
        radon_output: Raw output from radon cc command
    
    Returns:
        Dictionary containing:
            - average_complexity: Average complexity across all blocks
            - total_functions: Total number of analyzed blocks
            - blocks: List of complexity blocks with details
            - total_complexity: Sum of all complexity scores
    
    Raises:
        AnalysisError: If parsing fails critically
    """
    if not radon_output:
        logger.warning("Radon output is empty")
        return _empty_radon_result()
    
    # Only reject if output starts with a clear error marker (not if 'error' appears in analyzed code)
    first_line = radon_output.strip().split('\n')[0].strip()
    if first_line.startswith("Traceback") or first_line.startswith("ERROR:"):
        logger.warning(f"Radon output starts with error: {first_line[:200]}")
        return _empty_radon_result()
    
    try:
        lines = radon_output.strip().split('\n')
        blocks: List[Dict[str, Any]] = []
        total_complexity = 0
        current_file = None
        
        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            if not line_stripped:
                continue
            
            # File path lines don't start with spaces
            if not line.startswith(' ') and not line.startswith('\t'):
                current_file = line_stripped
                logger.debug(f"Processing file: {current_file}")
                continue
            
            # Function/method/class lines start with M, F, or C
            if line_stripped and line_stripped[0] in ['M', 'F', 'C']:
                try:
                    block = _parse_radon_line(line_stripped, current_file)
                    if block:
                        blocks.append(block)
                        total_complexity += block['complexity']
                        logger.debug(
                            f"Parsed block: {block['name']} "
                            f"(complexity: {block['complexity']}, grade: {block['grade']})"
                        )
                except Exception as e:
                    logger.warning(
                        f"Failed to parse radon line {line_num}: {line_stripped[:100]} - {e}"
                    )
                    continue
        
        function_count = len(blocks)
        avg_complexity = total_complexity / function_count if function_count > 0 else 0
        
        result = {
            "average_complexity": round(avg_complexity, 2),
            "total_functions": function_count,
            "blocks": blocks,
            "total_complexity": total_complexity
        }
        
        logger.info(
            f"Radon parsing complete: {function_count} blocks, "
            f"avg complexity {avg_complexity:.2f}"
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Radon parsing error: {e}", exc_info=True)
        # Return empty result instead of raising to allow analysis to continue
        return _empty_radon_result()


def _parse_radon_line(line: str, current_file: str) -> Dict[str, Any]:
    """
    Parse a single radon output line.
    
    Format: "F 12:0 function_name - A (3)"
    
    Args:
        line: Line to parse
        current_file: Current file being processed
    
    Returns:
        Dictionary with block details or None if parsing fails
    """
    # Parse format: "F 12:0 function_name - A (3)"
    parts = line.split(' - ')
    if len(parts) < 2:
        return None
    
    # Extract name from first part
    first_part = parts[0].strip()
    # Format: "F 12:0 function_name" or "M 45:4 ClassName.method_name"
    name_parts = first_part.split(' ', 2)
    
    if len(name_parts) < 3:
        return None
    
    block_type = name_parts[0]  # F, M, or C
    location = name_parts[1]    # line:column
    name = name_parts[2]        # function/method/class name
    
    # Extract complexity from second part: "A (3)"
    complexity_str = parts[1].strip()
    
    # Extract grade letter
    grade_match = re.match(r'^([A-F])', complexity_str)
    grade_letter = grade_match.group(1) if grade_match else 'F'
    
    # Extract number in parentheses
    complexity_match = re.search(r'\((\d+)\)', complexity_str)
    complexity = int(complexity_match.group(1)) if complexity_match else 1
    
    # Map block type
    block_type_map = {'F': 'function', 'M': 'method', 'C': 'class'}
    
    return {
        "name": name,
        "complexity": complexity,
        "grade": grade_letter,
        "type": block_type_map.get(block_type, 'function'),
        "file": current_file or "unknown",
        "location": location
    }


def _empty_radon_result() -> Dict[str, Any]:
    """Return empty radon result structure."""
    return {
        "average_complexity": 0,
        "total_functions": 0,
        "blocks": [],
        "total_complexity": 0
    }
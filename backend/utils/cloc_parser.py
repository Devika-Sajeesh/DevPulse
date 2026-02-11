"""
CLOC (Count Lines of Code) output parser.

Parses output from 'cloc' command with comprehensive error handling
and validation for both JSON and raw formats.
"""

from typing import Dict, Any
import json
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)


def parse_cloc_output(cloc_output: str) -> Dict[str, Any]:
    """
    Parse CLOC JSON output correctly.
    
    If using cloc with --json flag, output will be JSON format.
    Falls back to radon raw parsing if needed.
    
    Args:
        cloc_output: Raw output from cloc command
    
    Returns:
        Dictionary containing:
            - code: Total lines of code
            - comment: Total comment lines
            - blank: Total blank lines
            - languages: Per-language statistics
            - total_files: Total number of files
    """
    if not cloc_output:
        logger.warning("CLOC output is empty")
        return _empty_cloc_result()
    
    # Only reject if output starts with a clear error marker
    first_line = cloc_output.strip().split('\n')[0].strip()
    if first_line.startswith("Traceback") or first_line.startswith("ERROR:"):
        logger.warning(f"CLOC output starts with error: {first_line[:200]}")
        return _empty_cloc_result()

    try:
        # First, try to parse as JSON (if using cloc --json)
        if cloc_output.strip().startswith('{'):
            return _parse_cloc_json(cloc_output)
        
        # Fallback: Parse radon raw output
        logger.info("CLOC output is not JSON, trying radon raw format")
        return parse_radon_raw_output(cloc_output)
        
    except json.JSONDecodeError as e:
        # Not JSON, try radon raw format
        logger.info(f"CLOC JSON decode failed ({e}), trying radon raw format")
        return parse_radon_raw_output(cloc_output)
    except Exception as e:
        logger.error(f"CLOC parsing error: {e}", exc_info=True)
        return _empty_cloc_result()


def _parse_cloc_json(cloc_output: str) -> Dict[str, Any]:
    """
    Parse CLOC JSON format output.
    
    Args:
        cloc_output: JSON formatted CLOC output
    
    Returns:
        Parsed CLOC statistics
    """
    data = json.loads(cloc_output)
    
    # CLOC JSON format includes a 'header' and language breakdowns
    result = {
        "code": 0,
        "comment": 0,
        "blank": 0,
        "languages": {},
        "total_files": 0
    }
    
    for key, value in data.items():
        if key == 'header':
            result['total_files'] = value.get('n_files', 0)
            logger.debug(f"CLOC header: {value.get('n_files', 0)} files")
        elif key == 'SUM':
            result['code'] = value.get('code', 0)
            result['comment'] = value.get('comment', 0)
            result['blank'] = value.get('blank', 0)
            logger.debug(
                f"CLOC totals: code={result['code']}, "
                f"comment={result['comment']}, blank={result['blank']}"
            )
        elif isinstance(value, dict) and 'code' in value:
            # This is a language entry
            result['languages'][key] = {
                'code': value.get('code', 0),
                'comment': value.get('comment', 0),
                'blank': value.get('blank', 0),
                'files': value.get('nFiles', 0)
            }
            logger.debug(f"CLOC language {key}: {value.get('code', 0)} lines")
    
    logger.info(
        f"CLOC parsing complete: {result['total_files']} files, "
        f"{result['code']} lines of code"
    )
    
    return result


def parse_radon_raw_output(radon_output: str) -> Dict[str, Any]:
    """
    Parse output from 'radon raw' command (fallback).
    
    Expected format per file:
        filename
            LOC: 136
            LLOC: 69
            SLOC: 95
            Comments: 14
            Blank: 27
    
    Args:
        radon_output: Raw output from radon raw command
    
    Returns:
        Parsed statistics in CLOC format
    """
    total_code = 0
    total_comment = 0
    total_blank = 0
    files = 0
    
    lines = radon_output.splitlines()
    
    for line in lines:
        line = line.strip()
        
        # Count files (lines without leading spaces that aren't metrics)
        if line and not any(line.startswith(prefix) for prefix in [
            'LOC:', 'LLOC:', 'SLOC:', 'Comments:', 'Blank:', 'Multi:', 'Single'
        ]):
            if '/' in line or '\\' in line or line.endswith('.py'):
                files += 1
        
        # SLOC is Source Lines of Code (actual code)
        if line.startswith("SLOC:"):
            try:
                total_code += int(line.split(":")[1].strip())
            except (ValueError, IndexError) as e:
                logger.debug(f"Failed to parse SLOC line: {line} - {e}")
        elif line.startswith("Comments:"):
            try:
                total_comment += int(line.split(":")[1].strip())
            except (ValueError, IndexError) as e:
                logger.debug(f"Failed to parse Comments line: {line} - {e}")
        elif line.startswith("Blank:"):
            try:
                total_blank += int(line.split(":")[1].strip())
            except (ValueError, IndexError) as e:
                logger.debug(f"Failed to parse Blank line: {line} - {e}")

    result = {
        "code": total_code,
        "comment": total_comment,
        "blank": total_blank,
        "languages": {
            "Python": {
                "code": total_code, 
                "comment": total_comment, 
                "blank": total_blank,
                "files": files
            }
        },
        "total_files": files
    }
    
    logger.info(
        f"Radon raw parsing complete: {files} files, "
        f"{total_code} lines of code"
    )
    
    return result


def _empty_cloc_result() -> Dict[str, Any]:
    """Return empty CLOC result structure."""
    return {
        "code": 0,
        "comment": 0,
        "blank": 0,
        "languages": {},
        "total_files": 0
    }
from typing import Dict, Any
import json

def parse_cloc_output(cloc_output: str) -> Dict[str, Any]:
    """
    Parses CLOC JSON output correctly.
    
    If using cloc with --json flag, output will be JSON format.
    Falls back to radon raw parsing if needed.
    """
    if not cloc_output or "Error" in cloc_output:
        return {
            "code": 0,
            "comment": 0,
            "blank": 0,
            "languages": {},
            "total_files": 0
        }

    try:
        # First, try to parse as JSON (if using cloc --json)
        if cloc_output.strip().startswith('{'):
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
                elif key == 'SUM':
                    result['code'] = value.get('code', 0)
                    result['comment'] = value.get('comment', 0)
                    result['blank'] = value.get('blank', 0)
                elif isinstance(value, dict) and 'code' in value:
                    # This is a language entry
                    result['languages'][key] = {
                        'code': value.get('code', 0),
                        'comment': value.get('comment', 0),
                        'blank': value.get('blank', 0),
                        'files': value.get('nFiles', 0)
                    }
            
            return result
        
        # Fallback: Parse radon raw output
        return parse_radon_raw_output(cloc_output)
        
    except json.JSONDecodeError:
        # Not JSON, try radon raw format
        return parse_radon_raw_output(cloc_output)
    except Exception as e:
        print(f"[PARSER] CLOC parsing error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "code": 0,
            "comment": 0,
            "blank": 0,
            "languages": {},
            "total_files": 0
        }


def parse_radon_raw_output(radon_output: str) -> Dict[str, Any]:
    """
    Parses output from 'radon raw' command (fallback).
    
    Expected format per file:
    filename
        LOC: 136
        LLOC: 69
        SLOC: 95
        Comments: 14
        Blank: 27
    """
    total_code = 0
    total_comment = 0
    total_blank = 0
    files = 0
    
    lines = radon_output.splitlines()
    
    for line in lines:
        line = line.strip()
        
        # Count files (lines without leading spaces that aren't metrics)
        if line and not line.startswith('LOC:') and not line.startswith('LLOC:') \
           and not line.startswith('SLOC:') and not line.startswith('Comments:') \
           and not line.startswith('Blank:') and not line.startswith('Multi:') \
           and not line.startswith('Single'):
            if '/' in line or '\\' in line or line.endswith('.py'):
                files += 1
        
        # SLOC is Source Lines of Code (actual code)
        if line.startswith("SLOC:"):
            try:
                total_code += int(line.split(":")[1].strip())
            except: 
                pass
        elif line.startswith("Comments:"):
            try:
                total_comment += int(line.split(":")[1].strip())
            except: 
                pass
        elif line.startswith("Blank:"):
            try:
                total_blank += int(line.split(":")[1].strip())
            except: 
                pass

    return {
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
from typing import Dict, Any
import re

def parse_cloc_output(cloc_output: str) -> Dict[str, Any]:
    """
    Parses output from 'radon raw' command (used as fallback for cloc).
    
    Expected format per file:
    filename
        LOC: 136
        LLOC: 69
        SLOC: 95
        Comments: 14
        Single comments: 14
        Multi: 0
        Blank: 27
    """
    if not cloc_output or "Error" in cloc_output:
        return {"code": 0, "comment": 0, "blank": 0}

    total_code = 0
    total_comment = 0
    total_blank = 0
    
    # Regex to find blocks of stats
    # We look for lines like "    LOC: 123" etc.
    
    # Simple line-by-line parsing
    lines = cloc_output.splitlines()
    
    for line in lines:
        line = line.strip()
        if line.startswith("SLOC:"):
            # SLOC is roughly Source Lines of Code (code)
            try:
                total_code += int(line.split(":")[1].strip())
            except: pass
        elif line.startswith("Comments:"):
            try:
                total_comment += int(line.split(":")[1].strip())
            except: pass
        elif line.startswith("Blank:"):
            try:
                total_blank += int(line.split(":")[1].strip())
            except: pass

    return {
        "code": total_code,
        "comment": total_comment,
        "blank": total_blank,
        "languages": {"Python": {"code": total_code, "comment": total_comment, "blank": total_blank}}
    }
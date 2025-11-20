from typing import Dict, Any

def parse_radon_output(radon_output: str) -> Dict[str, Any]:
    """
    Parses radon cc output correctly.
    
    Expected format:
    path/to/file.py
        M 45:4 ClassName.method_name - B (6)
        F 12:0 function_name - A (3)
    """
    if not radon_output or "Error" in radon_output:
        print(f"[PARSER] Radon output empty or contains error")
        return {
            "average_complexity": 0,
            "total_functions": 0,
            "blocks": [],
            "total_complexity": 0
        }
    
    try:
        lines = radon_output.strip().split('\n')
        blocks = []
        total_complexity = 0
        current_file = None
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue
            
            # File path lines don't start with spaces
            if not line.startswith(' ') and not line.startswith('\t'):
                current_file = line_stripped
                continue
            
            # Function/method/class lines start with M, F, or C
            if line_stripped and line_stripped[0] in ['M', 'F', 'C']:
                try:
                    # Parse format: "F 12:0 function_name - A (3)"
                    parts = line_stripped.split(' - ')
                    if len(parts) < 2:
                        continue
                    
                    # Extract name from first part
                    first_part = parts[0].strip()
                    # Format: "F 12:0 function_name" or "M 45:4 ClassName.method_name"
                    name_parts = first_part.split(' ', 2)
                    if len(name_parts) >= 3:
                        block_type = name_parts[0]  # F, M, or C
                        name = name_parts[2]
                    else:
                        name = "unknown"
                    
                    # Extract complexity from second part: "A (3)"
                    complexity_str = parts[1].strip()
                    
                    # Extract grade letter and number
                    grade_letter = complexity_str.split()[0] if complexity_str else 'F'
                    
                    # Extract number in parentheses
                    import re
                    match = re.search(r'\((\d+)\)', complexity_str)
                    complexity = int(match.group(1)) if match else 1
                    
                    total_complexity += complexity
                    
                    block_type_map = {'F': 'function', 'M': 'method', 'C': 'class'}
                    
                    blocks.append({
                        "name": name,
                        "complexity": complexity,
                        "grade": grade_letter,
                        "type": block_type_map.get(block_type, 'function'),
                        "file": current_file or "unknown"
                    })
                    
                except Exception as e:
                    print(f"[PARSER] Failed to parse radon line: {line_stripped} - {e}")
                    continue
        
        function_count = len(blocks)
        avg_complexity = total_complexity / function_count if function_count > 0 else 0
        
        return {
            "average_complexity": round(avg_complexity, 2),
            "total_functions": function_count,
            "blocks": blocks,
            "total_complexity": total_complexity
        }
        
    except Exception as e:
        print(f"[PARSER] Radon parsing error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "average_complexity": 0,
            "total_functions": 0,
            "blocks": [],
            "total_complexity": 0
        }
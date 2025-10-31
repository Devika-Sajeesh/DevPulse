from typing import Dict, Any, Tuple

def parse_radon_output(radon_output: str) -> Dict[str, Any]:
    """Parse radon cyclomatic complexity output with better error handling"""
    if not radon_output or "Error" in radon_output:
        print(f"[PARSER] Radon output empty or contains error: {radon_output[:200] if radon_output else 'None'}")
        return {}
    
    try:
        # Radon cc output is text-based, not JSON
        lines = radon_output.strip().split('\n')
        total_complexity = 0
        function_count = 0
        blocks = []
        
        current_block = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for function definitions in radon output
            if '(' in line and ')' in line and ' - ' in line:
                # Example: "    function_name (path/to/file.py:10) - B (10)"
                parts = line.split(' - ')
                if len(parts) >= 2:
                    complexity_part = parts[-1]
                    if complexity_part.startswith('A '):
                        complexity = 1
                    elif complexity_part.startswith('B '):
                        complexity = 2  
                    elif complexity_part.startswith('C '):
                        complexity = 3
                    elif complexity_part.startswith('D '):
                        complexity = 4
                    elif complexity_part.startswith('E '):
                        complexity = 5
                    elif complexity_part.startswith('F '):
                        complexity = 6
                    else:
                        complexity = 1
                    
                    total_complexity += complexity
                    function_count += 1
                    blocks.append({
                        "name": parts[0].strip(),
                        "complexity": complexity,
                        "type": "function"
                    })
        
        avg_complexity = total_complexity / function_count if function_count > 0 else 0
        
        return {
            "average_complexity": round(avg_complexity, 2),
            "total_functions": function_count,
            "blocks": blocks,
            "total_complexity": total_complexity
        }
        
    except Exception as e:
        print(f"[PARSER] Radon parsing error: {e}")
        return {}
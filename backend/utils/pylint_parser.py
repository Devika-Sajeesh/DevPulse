def parse_pylint_output(output: str):
    """Parse pylint output with better error handling"""
    if not output or "Error" in output:
        print(f"[PARSER] Pylint output empty or contains error: {output[:200] if output else 'None'}")
        return {"score": 5.0, "issues": []}
    
    try:
        lines = [l for l in output.splitlines() if l.strip()]
        score = None
        issues = []
        
        for line in lines:
            # Look for the rating line
            if "Your code has been rated at" in line:
                import re
                m = re.search(r"rated at\s+([-+]?\d+\.\d+)/10", line)
                if m: 
                    score = float(m.group(1))
            # Collect issue lines (skip empty and rating lines)
            elif line.strip() and not line.startswith("---"):
                issues.append(line)
        
        # If no score found, default to 5.0
        if score is None:
            score = 5.0
            
        return {
            "score": score, 
            "issues": issues[-10:] if len(issues) > 10 else issues  # Keep last 10 issues
        }
        
    except Exception as e:
        print(f"[PARSER] Pylint parsing error: {e}")
        return {"score": 5.0, "issues": []}
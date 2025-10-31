from typing import Dict, Any, Tuple

def parse_cloc_output(cloc_output: str) -> Dict[str, Any]:
    """Parse cloc output with better error handling"""
    if not cloc_output or "Error" in cloc_output:
        print(f"[PARSER] CLOC output empty or contains error: {cloc_output[:200] if cloc_output else 'None'}")
        return {"code": 0, "comment": 0, "blank": 0}
    
    try:
        # Try to parse as JSON
        import json
        data = json.loads(cloc_output)
        
        # CLOC JSON structure has a "SUM" key with totals
        if "SUM" in data:
            sum_data = data["SUM"]
            return {
                "code": sum_data.get("code", 0),
                "comment": sum_data.get("comment", 0), 
                "blank": sum_data.get("blank", 0),
                "languages": data  # Include all language data
            }
        else:
            # If no SUM, calculate from individual languages
            total_code = 0
            total_comment = 0
            total_blank = 0
            
            for lang, stats in data.items():
                if lang != "header":
                    total_code += stats.get("code", 0)
                    total_comment += stats.get("comment", 0)
                    total_blank += stats.get("blank", 0)
            
            return {
                "code": total_code,
                "comment": total_comment,
                "blank": total_blank,
                "languages": data
            }
            
    except json.JSONDecodeError:
        print(f"[PARSER] CLOC output is not valid JSON: {cloc_output[:200]}")
        return {"code": 0, "comment": 0, "blank": 0}
    except Exception as e:
        print(f"[PARSER] CLOC parsing error: {e}")
        return {"code": 0, "comment": 0, "blank": 0}
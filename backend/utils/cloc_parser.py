import json

def parse_cloc_output(output: str):
    try:
        return json.loads(output)
    except Exception:
        return {"raw": output}

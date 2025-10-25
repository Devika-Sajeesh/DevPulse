def parse_radon_output(output: str):
    lines = [l.strip() for l in output.splitlines() if l.strip()]
    return {"entries": lines, "summary": lines[-1] if lines else None}

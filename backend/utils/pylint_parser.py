def parse_pylint_output(output: str):
    lines = [l for l in output.splitlines() if l.strip()]
    score = None
    for line in reversed(lines):
        if "Your code has been rated at" in line:
            import re
            m = re.search(r"rated at\s+([-+]?\d+\.\d+)/10", line)
            if m: score = float(m.group(1))
            break
    return {"score": score, "issues": lines[-5:]}  # keep only last 5 for brevity

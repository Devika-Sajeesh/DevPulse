# backend/services/analyzer.py

import asyncio
import tempfile
import shutil
import os
from typing import Dict, Any, Tuple
from concurrent.futures import ThreadPoolExecutor
import subprocess

from backend.utils.radon_parser import parse_radon_output
from backend.utils.cloc_parser import parse_cloc_output
from backend.utils.pylint_parser import parse_pylint_output
from backend.services.ai_summary import generate_ai_metrics # Changed name
from backend.utils.repo_downloader import clone_repo  
from backend.services.predictor import calculate_chs, get_historical_risk_score # New Import

from dotenv import load_dotenv
load_dotenv()

EXECUTOR = ThreadPoolExecutor(max_workers=4)


async def run_command_async(*args: str) -> str:
    """
    Run an external command asynchronously and return its stdout.
    Args are passed as individual strings, not lists.
    """
    loop = asyncio.get_running_loop()

    def _run():
        cmd = [str(a) for a in args]  
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout

    return await loop.run_in_executor(None, _run)


async def clone_repo_async(repo_url: str, dest_dir: str) -> Tuple[str, str]: # Return type updated
    loop = asyncio.get_running_loop()
    # clone_repo now returns (path, sha)
    return await loop.run_in_executor(EXECUTOR, clone_repo, repo_url, dest_dir) 

RADON_PATH = os.getenv("RADON_PATH", "radon")
PYLINT_PATH = os.getenv("PYLINT_PATH", "pylint")
CLOC_PATH = os.getenv("CLOC_PATH", "cloc")

async def analyze_single_repo(repo_url: str) -> Dict[str, Any]:
    temp_dir = tempfile.mkdtemp()
    try:
        # 1. Clone Repo and Get SHA
        repo_path, commit_sha = await clone_repo_async(repo_url, temp_dir) # Unpack path and SHA

        radon_cmd = [RADON_PATH, "cc", repo_path, "-s", "-a"]
        cloc_cmd = [CLOC_PATH, repo_path, "--json"]
        pylint_cmd = [PYLINT_PATH, repo_path, "-f", "text"]

        # 2. Run Static Analysis Tools
        radon_out, cloc_out, pylint_out = await asyncio.gather(
            run_command_async(*radon_cmd),
            run_command_async(*cloc_cmd),
            run_command_async(*pylint_cmd),
        )

        # 3. Parse outputs (w1 preparation)
        radon_parsed = parse_radon_output(radon_out) or {}
        cloc_parsed = parse_cloc_output(cloc_out) or {"code": 0, "comment": 0, "blank": 0}
        pylint_parsed = parse_pylint_output(pylint_out) or {"score": None, "messages": []}

        parsed = {
            "repo_url": repo_url,
            "git_sha": commit_sha, # New field
            "radon": radon_parsed,
            "cloc": cloc_parsed,
            "pylint": pylint_parsed,
        }

        # 4. Generate AI Metrics (w2)
        ai_metrics = await generate_ai_metrics(radon_out, cloc_out, pylint_out)
        
        # 5. Calculate Predictive Scores (w3 and CHS)
        ai_probability = ai_metrics.get("ai_probability", 0.0)
        historical_risk = get_historical_risk_score(repo_url, commit_sha) # Placeholder w3
        
        code_health_score = calculate_chs(parsed, ai_probability, historical_risk) # Final CHS

        # 6. Assemble Final Results
        parsed["ai_metrics"] = ai_metrics # New field
        parsed["code_health_score"] = code_health_score # New field
        parsed["historical_risk_score"] = historical_risk # New field

        return parsed

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
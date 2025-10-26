# backend/services/analyzer.py (Updated with Docker SDK logic)

import asyncio
import tempfile
import shutil
import os
from typing import Dict, Any, Tuple
from concurrent.futures import ThreadPoolExecutor
import subprocess
import time  # For unique volume naming
# Try to import the docker client (will only work if 'docker' is installed)
try:
    import docker 
    DOCKER_CLIENT = docker.from_env()
    DOCKER_SANDBOX_ENABLED = True
except ImportError:
    DOCKER_CLIENT = None
    DOCKER_SANDBOX_ENABLED = False


from backend.utils.radon_parser import parse_radon_output
from backend.utils.cloc_parser import parse_cloc_output
from backend.utils.pylint_parser import parse_pylint_output
from backend.services.ai_summary import generate_ai_metrics 
from backend.utils.repo_downloader import clone_repo 
from backend.services.predictor import calculate_chs, get_historical_risk_score, extract_features_for_prediction

from dotenv import load_dotenv
load_dotenv()

EXECUTOR = ThreadPoolExecutor(max_workers=4)

# Define the image that would execute the analysis commands securely
SANDBOX_IMAGE = os.getenv("SANDBOX_IMAGE", "python:3.11-slim") # Use slim python as a safe default

# --- NEW: Docker Sandboxed Command Execution Logic ---
async def run_sandboxed_command(*args: str, repo_path: str) -> str:
    """
    Executes a command inside an isolated Docker container if enabled, 
    otherwise falls back to insecure direct execution.
    """
    if not DOCKER_SANDBOX_ENABLED:
        print("WARNING: Docker Sandbox not available. Running analysis on host (INSECURE).")
        # FALLBACK TO ORIGINAL INSECURE EXECUTION
        loop = asyncio.get_running_loop()
        def _run():
            cmd = [str(a) for a in args]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.stdout
        return await loop.run_in_executor(None, _run)

    # SECURE EXECUTION LOGIC (Conceptual with DOCKER SDK)
    loop = asyncio.get_running_loop()
    
    # Generate a unique volume name to mount the repository safely
    volume_name = f"devpulse-analysis-{time.time_ns()}"

    def _run_in_docker():
        # The target code path INSIDE the container is fixed as /repo
        container_repo_path = "/repo"
        
        # 1. Prepare command with the container path
        cmd_for_docker = [str(a).replace(repo_path, container_repo_path) for a in args]
        
        # 2. Run the command in an ephemeral container
        try:
            # Mount the host directory (repo_path) to the container path (/repo)
            container = DOCKER_CLIENT.containers.run(
                SANDBOX_IMAGE,
                command=cmd_for_docker,
                volumes={repo_path: {'bind': container_repo_path, 'mode': 'ro'}},
                remove=True,  # Automatically remove container on exit
                detach=False, # Wait for command to complete
                user=1000     # Run as a non-root user (good practice)
            )
            return container.decode('utf-8')

        except Exception as e:
            return f"Error executing sandboxed command: {e}"
            
    # Run the synchronous Docker call in a separate thread
    return await loop.run_in_executor(EXECUTOR, _run_in_docker)


async def clone_repo_async(repo_url: str, dest_dir: str) -> Tuple[str, str]:
    loop = asyncio.get_running_loop()
    # clone_repo now returns (path, sha)
    return await loop.run_in_executor(EXECUTOR, clone_repo, repo_url, dest_dir) 

# The old run_command_async function is now implicitly replaced by run_sandboxed_command.

RADON_PATH = os.getenv("RADON_PATH", "radon")
PYLINT_PATH = os.getenv("PYLINT_PATH", "pylint")
CLOC_PATH = os.getenv("CLOC_PATH", "cloc")

async def analyze_single_repo(repo_url: str) -> Dict[str, Any]:
    temp_dir = tempfile.mkdtemp()
    try:
        # 1. Clone Repo and Get SHA (Still done on the host for simplicity in this version)
        repo_path, commit_sha = await clone_repo_async(repo_url, temp_dir) 

        # 2. Define commands relative to the cloned path
        radon_cmd = [RADON_PATH, "cc", repo_path, "-s", "-a"]
        cloc_cmd = [CLOC_PATH, repo_path, "--json"]
        pylint_cmd = [PYLINT_PATH, repo_path, "-f", "text"]
        
        # 3. Run Static Analysis Tools conceptually sandboxed
        radon_out, cloc_out, pylint_out = await asyncio.gather(
            run_sandboxed_command(*radon_cmd, repo_path=repo_path),
            run_sandboxed_command(*cloc_cmd, repo_path=repo_path),
            run_sandboxed_command(*pylint_cmd, repo_path=repo_path),
        )

       
        
        # 4. Parse outputs (w1 preparation)
        radon_parsed = parse_radon_output(radon_out) or {}
        cloc_parsed = parse_cloc_output(cloc_out) or {"code": 0, "comment": 0, "blank": 0}
        pylint_parsed = parse_pylint_output(pylint_out) or {"score": None, "messages": []}

        parsed = {
            "repo_url": repo_url,
            "git_sha": commit_sha,
            "radon": radon_parsed,
            "cloc": cloc_parsed,
            "pylint": pylint_parsed,
        }

        
        # 5. Generate AI Metrics (w2)
        ai_metrics = await generate_ai_metrics(radon_out, cloc_out, pylint_out)
        
        # 6. Calculate Predictive Scores (w3 and CHS)
        ai_probability = ai_metrics.get("ai_probability", 0.0)
        
        feature_vector = extract_features_for_prediction(parsed, ai_probability)
        
        historical_risk = get_historical_risk_score(repo_url, commit_sha, feature_vector)
        
        code_health_score = calculate_chs(parsed, ai_probability, historical_risk)

        # 7. Assemble Final Results
        parsed["ai_metrics"] = ai_metrics 
        parsed["code_health_score"] = code_health_score 
        parsed["historical_risk_score"] = historical_risk 

        return parsed

    finally:
        # Cleanup: Remove the temporary host directory after analysis
        shutil.rmtree(temp_dir, ignore_errors=True)
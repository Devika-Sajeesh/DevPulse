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
SANDBOX_IMAGE = os.getenv("SANDBOX_IMAGE", "devpulse-sandbox") 
SANDBOX_IMAGE = os.getenv("SANDBOX_IMAGE", "python:3.11-slim")
print(f"[SANDBOX] Using Docker image: {SANDBOX_IMAGE}")


async def run_sandboxed_command(*args: str, repo_path: str) -> str:
    """
    Executes a command inside an isolated Docker container if enabled, 
    otherwise falls back to insecure direct execution.
    """
    if not DOCKER_SANDBOX_ENABLED:
        print(f"[SANDBOX] Running on host: {' '.join(args)}")
        loop = asyncio.get_running_loop()
        def _run():
            try:
                cmd = [str(a) for a in args]
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=repo_path, timeout=120)
                if result.returncode != 0:
                    print(f"[SANDBOX] Command failed (code {result.returncode}): {result.stderr}")
                    return f""
                return result.stdout
            except subprocess.TimeoutExpired:
                print(f"[SANDBOX] Command timed out")
                return ""
            except Exception as e:
                print(f"[SANDBOX] Host execution error: {e}")
                return ""
        return await loop.run_in_executor(EXECUTOR, _run)

    # Docker execution
    print(f"[SANDBOX] Running in Docker: {' '.join(args)}")
    loop = asyncio.get_running_loop()

    def _run_in_docker():
        container_repo_path = "/repo"
        
        # Build command for docker - use relative paths inside container
        cmd_for_docker = []
        for arg in args:
            # Replace the repo path with the container path
            if os.path.abspath(str(arg)) == os.path.abspath(repo_path):
                cmd_for_docker.append(container_repo_path)
            else:
                cmd_for_docker.append(str(arg))
        
        print(f"[SANDBOX] Docker command: {cmd_for_docker}")
        print(f"[SANDBOX] Mounting: {repo_path} -> {container_repo_path}")
        
        try:
            # Ensure the repo directory exists and has proper permissions
            if not os.path.exists(repo_path):
                raise Exception(f"Repo path does not exist: {repo_path}")
                
            container_output = DOCKER_CLIENT.containers.run(
                SANDBOX_IMAGE,
                command=cmd_for_docker,
                volumes={repo_path: {'bind': container_repo_path, 'mode': 'ro'}},
                working_dir=container_repo_path,
                remove=True,
                detach=False,
                stdout=True,
                stderr=True,
                user="root",  # Use root to avoid permission issues
                mem_limit="512m",  # Add memory limit
                network_mode="none"  # Disable network for security
            )
            
            output = container_output.decode('utf-8') if isinstance(container_output, bytes) else str(container_output)
            print(f"[SANDBOX] Command successful, output length: {len(output)}")
            return output
            
        except docker.errors.ContainerError as e:
            error_msg = e.stderr.decode('utf-8') if e.stderr else str(e)
            print(f"[SANDBOX] Container error: {error_msg}")
            return ""
        except docker.errors.ImageNotFound:
            print(f"[SANDBOX] Image not found: {SANDBOX_IMAGE}")
            return ""
        except Exception as e:
            print(f"[SANDBOX] Docker execution error: {str(e)}")
            return ""
            
    return await loop.run_in_executor(EXECUTOR, _run_in_docker)


async def clone_repo_async(repo_url: str, dest_dir: str) -> Tuple[str, str]:
    loop = asyncio.get_running_loop()
    # clone_repo now returns (path, sha)
    return await loop.run_in_executor(EXECUTOR, clone_repo, repo_url, dest_dir) 

# The old run_command_async function is now implicitly replaced by run_sandboxed_command.

RADON_PATH = "radon"
PYLINT_PATH = "pylint"
CLOC_PATH = "cloc"

# In analyzer.py - UPDATED analyze_single_repo function
async def analyze_single_repo(repo_url: str) -> Dict[str, Any]:
    temp_dir = tempfile.mkdtemp()
    print(f"[ANALYZER] Starting analysis for: {repo_url}")
    print(f"[ANALYZER] Using temp directory: {temp_dir}")
    
    try:
        # 1. Clone Repo
        print(f"[ANALYZER] Cloning repository...")
        repo_path, commit_sha = await clone_repo_async(repo_url, temp_dir)
        print(f"[ANALYZER] Cloned to: {repo_path}, SHA: {commit_sha}")
        
        # Verify clone was successful
        if not repo_path or not os.path.exists(repo_path):
            raise Exception(f"Repository clone failed for: {repo_url}")

        # 2. Define commands
        radon_cmd = [RADON_PATH, "cc", ".", "-s", "-a"]
        cloc_cmd = [CLOC_PATH, ".", "--json"]
        pylint_cmd = [PYLINT_PATH, ".", "-f", "json", "--exit-zero"]  # Changed to JSON format for easier parsing
        
        print(f"[ANALYZER] Running analysis tools...")
        
        # 3. Run tools with better error handling
        try:
            radon_out, cloc_out, pylint_out = await asyncio.gather(
                run_sandboxed_command(*radon_cmd, repo_path=repo_path),
                run_sandboxed_command(*cloc_cmd, repo_path=repo_path),
                run_sandboxed_command(*pylint_cmd, repo_path=repo_path),
                return_exceptions=True  # This prevents one failure from stopping all
            )
        except Exception as e:
            print(f"[ANALYZER] Tool execution failed: {e}")
            raise

        # 4. Handle individual tool failures
        tools_output = []
        for name, output in [("radon", radon_out), ("cloc", cloc_out), ("pylint", pylint_out)]:
            if isinstance(output, Exception):
                print(f"[ANALYZER] {name} failed: {output}")
                tools_output.append("")
            else:
                print(f"[ANALYZER] {name} output length: {len(str(output))}")
                tools_output.append(output)

        radon_out, cloc_out, pylint_out = tools_output

        # 5. Parse outputs with fallbacks
        print(f"[ANALYZER] Parsing results...")
        radon_parsed = parse_radon_output(radon_out) if radon_out else {}
        cloc_parsed = parse_cloc_output(cloc_out) if cloc_out else {"code": 0, "comment": 0, "blank": 0}
        pylint_parsed = parse_pylint_output(pylint_out) if pylint_out else {"score": 5.0, "messages": []}
        
        # Ensure pylint score exists
        if pylint_parsed.get("score") is None:
            pylint_parsed["score"] = 5.0

        parsed = {
            "repo_url": repo_url,
            "git_sha": commit_sha,
            "radon": radon_parsed,
            "cloc": cloc_parsed,
            "pylint": pylint_parsed,
        }

        print(f"[ANALYZER] Basic parsing complete. Generating AI metrics...")
        
        # 6. Generate AI Metrics with error handling
        try:
            ai_metrics = await generate_ai_metrics(radon_out, cloc_out, pylint_out)
        except Exception as e:
            print(f"[ANALYZER] AI metrics generation failed: {e}")
            ai_metrics = {"ai_probability": 0.0, "summary": "AI analysis failed"}

        # 7. Calculate Predictive Scores
        ai_probability = ai_metrics.get("ai_probability", 0.0)
        
        try:
            feature_vector = extract_features_for_prediction(parsed, ai_probability)
            historical_risk = get_historical_risk_score(repo_url, commit_sha, feature_vector)
            code_health_score = calculate_chs(parsed, ai_probability, historical_risk)
        except Exception as e:
            print(f"[ANALYZER] Score calculation failed: {e}")
            historical_risk = 0.5
            code_health_score = 50.0

        # 8. Assemble Final Results
        parsed["ai_metrics"] = ai_metrics 
        parsed["code_health_score"] = code_health_score 
        parsed["historical_risk_score"] = historical_risk

        print(f"[ANALYZER] Analysis complete. CHS: {code_health_score}")
        return parsed

    except Exception as e:
        print(f"[ANALYZER] Critical error in analysis: {e}")
        import traceback
        traceback.print_exc()
        # Return a minimal valid response instead of None
        return {
            "repo_url": repo_url,
            "git_sha": "unknown",
            "radon": {},
            "cloc": {"code": 0, "comment": 0, "blank": 0},
            "pylint": {"score": 5.0, "messages": []},
            "ai_metrics": {"ai_probability": 0.0, "summary": "Analysis failed"},
            "code_health_score": 0.0,
            "historical_risk_score": 1.0
        }
    finally:
        # Cleanup
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
            print(f"[ANALYZER] Cleaned up temp directory: {temp_dir}")
        except Exception as e:
            print(f"[ANALYZER] Cleanup warning: {e}")
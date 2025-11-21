# backend/services/analyzer.py (Critical Fixes)

import asyncio
import tempfile
import shutil
import os
from typing import Dict, Any, Tuple
from concurrent.futures import ThreadPoolExecutor

try:
    import docker 
    try:
        DOCKER_CLIENT = docker.from_env()
        DOCKER_SANDBOX_ENABLED = True
    except Exception as e:
        print(f"[WARNING] Docker not available: {e}")
        DOCKER_CLIENT = None
        DOCKER_SANDBOX_ENABLED = False
except ImportError:
    DOCKER_CLIENT = None
    DOCKER_SANDBOX_ENABLED = False

from backend.services.ai_summary import generate_ai_metrics 
from backend.utils.repo_downloader import clone_repo 
from backend.services.predictor import calculate_chs, get_historical_risk_score, extract_features_for_prediction
from backend.utils.radon_parser import parse_radon_output
from backend.utils.cloc_parser import parse_cloc_output
from backend.utils.pylint_parser import parse_pylint_output

from dotenv import load_dotenv
load_dotenv()

EXECUTOR = ThreadPoolExecutor(max_workers=4)
SANDBOX_IMAGE = os.getenv("SANDBOX_IMAGE", "devpulse-sandbox")

print(f"[SANDBOX] Using Docker image: {SANDBOX_IMAGE}")
print(f"[SANDBOX] Docker enabled: {DOCKER_SANDBOX_ENABLED}")


async def run_sandboxed_command(*args: str, repo_path: str) -> str:
    """Executes a command inside Docker container or on host."""
    
    if not DOCKER_SANDBOX_ENABLED:
        print(f"[SANDBOX] Running on host: {' '.join(args)}")
        loop = asyncio.get_running_loop()
        def _run():
            try:
                import subprocess
                cmd = [str(a) for a in args]
                use_shell = os.name == 'nt'
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    cwd=repo_path, 
                    timeout=120, 
                    shell=use_shell
                )
                if result.returncode != 0 and result.returncode != 1:
                    # Note: pylint returns non-zero for issues, which is normal
                    print(f"[SANDBOX] Command returned code {result.returncode}")
                    print(f"[SANDBOX] stderr: {result.stderr[:500]}")
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
        
        cmd_for_docker = []
        for arg in args:
            if arg == '.':
                cmd_for_docker.append(container_repo_path)
            elif os.path.isabs(str(arg)) and os.path.abspath(str(arg)) == os.path.abspath(repo_path):
                cmd_for_docker.append(container_repo_path)
            else:
                cmd_for_docker.append(str(arg))
        
        print(f"[SANDBOX] Docker command: {cmd_for_docker}")
        
        try:
            if not os.path.exists(repo_path):
                raise Exception(f"Repo path does not exist: {repo_path}")
            
            try:
                output = DOCKER_CLIENT.containers.run(
                    SANDBOX_IMAGE,
                    command=cmd_for_docker,
                    volumes={repo_path: {'bind': container_repo_path, 'mode': 'ro'}},
                    working_dir=container_repo_path,
                    remove=True,
                    detach=False,
                    stdout=True,
                    stderr=True,
                    user="root",
                    mem_limit="512m",
                    network_mode="none"
                )
                
                if isinstance(output, bytes):
                    result = output.decode('utf-8', errors='ignore')
                else:
                    result = str(output)
                    
                print(f"[SANDBOX] Command successful, output length: {len(result)}")
                return result
                
            except docker.errors.ContainerError as e:
                error_msg = e.stderr.decode('utf-8', errors='ignore') if e.stderr else str(e)
                print(f"[SANDBOX] Container error (exit {e.exit_status}): {error_msg[:200]}")
                
                # For tools like pylint, non-zero exit is normal
                stdout = getattr(e, 'stdout', b'')
                if stdout:
                    return stdout.decode('utf-8', errors='ignore')
                return ""
                
        except docker.errors.ImageNotFound:
            print(f"[SANDBOX] Image not found: {SANDBOX_IMAGE}")
            return ""
        except Exception as e:
            print(f"[SANDBOX] Docker error: {str(e)}")
            import traceback
            traceback.print_exc()
            return ""
            
    return await loop.run_in_executor(EXECUTOR, _run_in_docker)


async def clone_repo_async(repo_url: str, dest_dir: str) -> Tuple[str, str]:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(EXECUTOR, clone_repo, repo_url, dest_dir)


async def analyze_single_repo(repo_url: str) -> Dict[str, Any]:
    temp_dir = tempfile.mkdtemp()
    print(f"\n{'='*70}")
    print(f"[ANALYZER] Starting analysis for: {repo_url}")
    print(f"[ANALYZER] Temp directory: {temp_dir}")
    print(f"{'='*70}\n")
    
    try:
        # 1. Clone repository
        print(f"[ANALYZER] Step 1: Cloning repository...")
        repo_path, commit_sha = await clone_repo_async(repo_url, temp_dir)
        print(f"[ANALYZER] ✓ Cloned to: {repo_path}")
        print(f"[ANALYZER] ✓ Commit SHA: {commit_sha}\n")
        
        if not repo_path or not os.path.exists(repo_path):
            raise Exception(f"Repository clone failed")

        # 2. Define tool commands
        # IMPORTANT: Use specific paths and flags that work reliably
        radon_cmd = [r"C:\Users\acer\AppData\Local\Programs\Python\Python313\python.exe", "-m", "radon", "cc", ".", "-s", "-a"]  # Cyclomatic complexity
        cloc_cmd = ["cloc", ".", "--json"]  # JSON output for easier parsing
        pylint_cmd = [r"C:\Users\acer\AppData\Local\Programs\Python\Python313\python.exe", "-m", "pylint", ".", "--output-format=text", "--exit-zero"]
        
        print(f"[ANALYZER] Step 2: Running analysis tools...")
        print(f"  - Radon: {' '.join(radon_cmd)}")
        print(f"  - CLOC: {' '.join(cloc_cmd)}")
        print(f"  - Pylint: {' '.join(pylint_cmd)}\n")
        
        # 3. Run all tools concurrently
        try:
            results = await asyncio.gather(
                run_sandboxed_command(*radon_cmd, repo_path=repo_path),
                run_sandboxed_command(*cloc_cmd, repo_path=repo_path),
                run_sandboxed_command(*pylint_cmd, repo_path=repo_path),
                return_exceptions=True
            )
            
            radon_out, cloc_out, pylint_out = results
            
        except Exception as e:
            print(f"[ANALYZER] ✗ Tool execution failed: {e}")
            radon_out, cloc_out, pylint_out = "", "", ""

        # 4. Log raw outputs for debugging
        print(f"[ANALYZER] Step 3: Processing tool outputs...")
        for name, output in [("Radon", radon_out), ("CLOC", cloc_out), ("Pylint", pylint_out)]:
            if isinstance(output, Exception):
                print(f"  ✗ {name}: FAILED - {output}")
            elif output:
                print(f"  ✓ {name}: {len(str(output))} chars")
                print(f"    Preview: {str(output)[:150]}...")
            else:
                print(f"  ⚠ {name}: Empty output")
        print()

        # 5. Parse tool outputs
        print(f"[ANALYZER] Step 4: Parsing results...")
        radon_parsed = parse_radon_output(radon_out if not isinstance(radon_out, Exception) else "")
        cloc_parsed = parse_cloc_output(cloc_out if not isinstance(cloc_out, Exception) else "")
        pylint_parsed = parse_pylint_output(pylint_out if not isinstance(pylint_out, Exception) else "")
        
        # Ensure required fields exist
        if not radon_parsed:
            radon_parsed = {"average_complexity": 0, "total_functions": 0, "blocks": [], "total_complexity": 0}
        if not cloc_parsed:
            cloc_parsed = {"code": 0, "comment": 0, "blank": 0, "languages": {}, "total_files": 0}
        if "score" not in pylint_parsed or pylint_parsed["score"] is None:
            pylint_parsed["score"] = 5.0
        
        print(f"  ✓ Radon: {radon_parsed.get('total_functions', 0)} functions, avg complexity {radon_parsed.get('average_complexity', 0)}")
        print(f"  ✓ CLOC: {cloc_parsed.get('code', 0)} lines of code, {cloc_parsed.get('total_files', 0)} files")
        print(f"  ✓ Pylint: Score {pylint_parsed.get('score', 0)}/10\n")

        parsed = {
            "repo_url": repo_url,
            "git_sha": commit_sha,
            "radon": radon_parsed,
            "cloc": cloc_parsed,
            "pylint": pylint_parsed,
        }

        # 6. Generate AI metrics
        print(f"[ANALYZER] Step 5: Generating AI insights...")
        try:
            ai_metrics = await generate_ai_metrics(
                str(radon_out) if radon_out else "", 
                str(cloc_out) if cloc_out else "", 
                str(pylint_out) if pylint_out else ""
            )
            print(f"  ✓ AI Probability: {ai_metrics.get('ai_probability', 0):.2%}")
            print(f"  ✓ Risk Notes: {ai_metrics.get('ai_risk_notes', 'N/A')}\n")
        except Exception as e:
            print(f"  ✗ AI metrics generation failed: {e}\n")
            ai_metrics = {
                "ai_probability": 0.0, 
                "ai_risk_notes": "AI analysis unavailable", 
                "recommendations": []
            }

        # 7. Calculate predictive scores
        print(f"[ANALYZER] Step 6: Calculating predictive scores...")
        try:
            ai_probability = ai_metrics.get("ai_probability", 0.0)
            feature_vector = extract_features_for_prediction(parsed, ai_probability)
            historical_risk = get_historical_risk_score(repo_url, commit_sha, feature_vector)
            code_health_score = calculate_chs(parsed, ai_probability, historical_risk)
            
            print(f"  ✓ Code Health Score: {code_health_score}/100")
            print(f"  ✓ Historical Risk: {historical_risk:.2%}\n")
        except Exception as e:
            print(f"  ✗ Score calculation failed: {e}\n")
            import traceback
            traceback.print_exc()
            historical_risk = 0.5
            code_health_score = 50.0

        # 8. Assemble final results
        parsed["ai_metrics"] = ai_metrics
        parsed["code_health_score"] = code_health_score
        parsed["historical_risk_score"] = historical_risk

        print(f"{'='*70}")
        print(f"[ANALYZER] ✓ Analysis Complete!")
        print(f"  • Code Health Score: {code_health_score}/100")
        print(f"  • AI Code Probability: {ai_probability:.1%}")
        print(f"  • Historical Risk: {historical_risk:.1%}")
        print(f"{'='*70}\n")
        
        return parsed

    except Exception as e:
        print(f"\n{'='*70}")
        print(f"[ANALYZER] ✗ CRITICAL ERROR: {e}")
        print(f"{'='*70}\n")
        import traceback
        traceback.print_exc()
        
        # Return minimal valid response
        return {
            "repo_url": repo_url,
            "git_sha": "unknown",
            "radon": {"average_complexity": 0, "total_functions": 0, "blocks": [], "total_complexity": 0},
            "cloc": {"code": 0, "comment": 0, "blank": 0, "languages": {}, "total_files": 0},
            "pylint": {"score": 0.0, "issues": []},
            "ai_metrics": {"ai_probability": 0.0, "ai_risk_notes": "Analysis failed", "recommendations": []},
            "code_health_score": 0.0,
            "historical_risk_score": 1.0
        }
    finally:
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
            print(f"[ANALYZER] Cleaned up: {temp_dir}\n")
        except Exception as e:
            print(f"[ANALYZER] Cleanup warning: {e}\n")
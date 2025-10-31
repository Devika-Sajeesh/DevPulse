# backend/main.py

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import traceback

from backend.services.analyzer import analyze_single_repo
from backend.utils.translator import get_translation
from backend.services.db_service import init_db, save_report, list_reports, get_report
from backend.services.predictor import load_ml_model

# Init app
app = FastAPI()

# Init DB on startup
init_db() # Run this once to update the schema! If you have old data, you might need to drop the table first.
load_ml_model()

# CORS for frontend
origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request schema
class RepoRequest(BaseModel):
    repo_url: str

# -------------------------------
#  ROUTES
# -------------------------------

# In main.py - update the analyze endpoint
@app.post("/analyze")
async def analyze(request: RepoRequest):
    try:
        print(f"[API] Starting analysis for: {request.repo_url}")
        results = await analyze_single_repo(request.repo_url)
        
        # Check if analysis returned valid results
        if results is None:
            raise HTTPException(status_code=500, detail="Analysis returned no results")
        
        print(f"[API] Analysis completed, saving to DB...")
        
        # Save to DB
        report_id = save_report(
            results["repo_url"],
            results["git_sha"],
            results["radon"],
            results["cloc"],
            results["pylint"],
            results["ai_metrics"],
            results["code_health_score"],
            results["historical_risk_score"],
        )
        
        print(f"[API] Report saved with ID: {report_id}")
        return {"report_id": report_id, "results": results}
        
    except Exception as e:
        print(f"[API] Analysis endpoint error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reports")
def reports():
    return list_reports()


@app.get("/reports/{report_id}")
def report(report_id: int):
    report = get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@app.get("/status")
async def status(translations: dict = Depends(get_translation)):
    return {"message": translations["analysis_complete"]}


@app.get("/upload")
async def upload(translations: dict = Depends(get_translation)):
    return {"message": translations["upload_prompt"]}

@app.get("/debug-tools")
async def debug_tools():
    """Debug endpoint to test if analysis tools are working"""
    import tempfile
    import os
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a test Python file
        test_file = os.path.join(tmpdir, "test.py")
        with open(test_file, "w") as f:
            f.write('''
def simple_function(x):
    """A simple function for testing"""
    return x + 1

class TestClass:
    def method(self):
        return "hello"
''')
        
        from backend.services.analyzer import run_sandboxed_command
        
        # Test each tool
        results = {}
        for tool, cmd in [
            ("radon", ["radon", "cc", ".", "-s", "-a"]),
            ("cloc", ["cloc", ".", "--json"]),
            ("pylint", ["pylint", ".", "-f", "text", "--exit-zero"])
        ]:
            try:
                output = await run_sandboxed_command(*cmd, repo_path=tmpdir)
                results[tool] = {
                    "status": "success",
                    "output_length": len(str(output)),
                    "output_preview": str(output)[:500] + "..." if len(str(output)) > 500 else str(output)
                }
            except Exception as e:
                results[tool] = {
                    "status": "error", 
                    "error": str(e)
                }
        
        return results
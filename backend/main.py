from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import traceback

from backend.services.analyzer import analyze_single_repo
from backend.utils.translator import get_translation
from backend.services.db_service import init_db, save_report, list_reports, get_report

# Init app
app = FastAPI()

# Init DB on startup
init_db()

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

@app.post("/analyze")
async def analyze(request: RepoRequest):
    try:
        results = await analyze_single_repo(request.repo_url)
        # Save to DB
        report_id = save_report(
            request.repo_url,
            results["radon"],
            results["cloc"],
            results["pylint"],
            results["ai_summary"],
        )
        return {"report_id": report_id, "results": results}
    except Exception as e:
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

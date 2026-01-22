from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

# Import services
from services.github_service import fetch_github_issue
from services.llm_service import analyze_with_gemini

app = FastAPI(
    title="GitHub Issue Analyzer API",
    description="API to fetching GitHub issues and analyzing them with Gemini AI",
    version="1.0.0"
)

# ====== CORS Settings ======
# Required for Streamlit to communicate with FastAPI if running on different ports/domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- Request Model ----------------
class AnalyzeRequest(BaseModel):
    repo_url: str
    issue_number: int

# ---------------- API Endpoints ----------------
@app.get("/")
def home():
    return {"message": "GitHub Issue Analyzer API is running. use /analyze to process issues."}

@app.post("/analyze")
async def analyze(data: AnalyzeRequest):
    """
    Endpoint to analyze a GitHub issue.
    1. Fetches issue content from GitHub API.
    2. Sends content to Gemini LLM for analysis.
    3. Returns JSON classification.
    """
    try:
        # Step 1: Fetch Data
        issue_text = fetch_github_issue(data.repo_url, data.issue_number)
        
        # Step 2: Analyze with LLM
        analysis = analyze_with_gemini(issue_text)
        
        return analysis
        
    except ValueError as ve:
        # Handle known errors (invalid URL, issue not found)
        raise HTTPException(status_code=400, detail=str(ve))
        
    except requests.exceptions.RequestException as re:
        # Handle network/external API errors
        raise HTTPException(status_code=502, detail=f"External API Error: {str(re)}")
        
    except Exception as e:
        # Handle unexpected server errors
        print(f"Server Error: {e}") # Log to console
        raise HTTPException(status_code=500, detail="Internal Server Error")

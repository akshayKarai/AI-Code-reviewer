"""
AI Code Reviewer — FastAPI Backend
Powered by Anthropic Claude for intelligent code analysis
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

from reviewer import CodeReviewer

app = FastAPI(
    title="AI Code Reviewer API",
    description="Intelligent code review powered by Claude AI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

reviewer = CodeReviewer()


# ── Request / Response models ──────────────────────────────────────────────────

class ReviewRequest(BaseModel):
    code: str
    language: Optional[str] = "auto"
    focus: Optional[list[str]] = ["bugs", "security", "performance", "style", "best_practices"]
    severity_filter: Optional[str] = "all"   # all | critical | major


class IssueItem(BaseModel):
    severity: str        # critical | major | minor | suggestion
    category: str        # bug | security | performance | style | best_practice
    line: Optional[str]
    title: str
    description: str
    suggestion: str


class ReviewResponse(BaseModel):
    language: str
    overall_score: int           # 0–100
    summary: str
    issues: list[IssueItem]
    positive_aspects: list[str]
    refactored_snippet: Optional[str]
    stats: dict


class ExplainRequest(BaseModel):
    code: str
    language: Optional[str] = "auto"


class ExplainResponse(BaseModel):
    explanation: str
    language: str


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "AI Code Reviewer API is running 🚀", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "healthy", "model": reviewer.model}


@app.get("/languages")
def supported_languages():
    return {"languages": reviewer.SUPPORTED_LANGUAGES}


@app.post("/review", response_model=ReviewResponse)
def review_code(request: ReviewRequest):
    """Submit code for a full AI-powered review."""
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty.")
    if len(request.code) > 20_000:
        raise HTTPException(status_code=400, detail="Code exceeds 20,000 character limit.")

    try:
        result = reviewer.review(
            code=request.code,
            language=request.language,
            focus=request.focus,
            severity_filter=request.severity_filter,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Review failed: {str(e)}")


@app.post("/explain", response_model=ExplainResponse)
def explain_code(request: ExplainRequest):
    """Get a plain-English explanation of what the code does."""
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty.")

    try:
        result = reviewer.explain(code=request.code, language=request.language)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explanation failed: {str(e)}")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

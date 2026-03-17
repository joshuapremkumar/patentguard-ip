"""
PatentGuard IP — FastAPI Backend
Exposes POST /analyze to orchestrate patent search and novelty scoring.
"""

import logging
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from agents.patent_search_agent import search_patents, TinyFishError
from services.novelty_engine import calculate_novelty_score

# Load environment variables from .env file
load_dotenv()

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ── App Init ───────────────────────────────────────────────────────────────────
app = FastAPI(
    title="PatentGuard IP API",
    version="1.0.0",
    description="AI-powered patent novelty analysis backend.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten in production
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Schemas ────────────────────────────────────────────────────────────────────
class AnalyzeRequest(BaseModel):
    """Request body for POST /analyze."""
    idea: str = Field(..., min_length=10, description="Invention description (min 10 chars)")


class AnalyzeResponse(BaseModel):
    """Response body for POST /analyze."""
    novelty_score: int          # 0–100; higher = more novel
    similar_patents: list[dict] # List of { title: str, link: str }


# ── Routes ─────────────────────────────────────────────────────────────────────
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_invention(body: AnalyzeRequest):
    """
    Analyze an invention idea:
    1. Run Patent Search Agent via TinyFish.
    2. Calculate novelty score.
    3. Return structured results.
    """
    logger.info("Received analyze request for idea: %s", body.idea[:80])

    # Step 1 — Patent Search
    try:
        search_result = await search_patents(body.idea)
    except TinyFishError as exc:
        logger.error("TinyFish API failure: %s", exc)
        raise HTTPException(status_code=502, detail=f"Patent search service unavailable: {exc}")
    except Exception as exc:
        logger.exception("Unexpected error during patent search")
        raise HTTPException(status_code=500, detail="Internal server error")

    patents = search_result.get("patents", [])
    logger.info("Found %d patents for query.", len(patents))

    # Step 2 — Novelty Scoring
    novelty_score = calculate_novelty_score(body.idea, patents)
    logger.info("Novelty score: %d", novelty_score)

    return AnalyzeResponse(novelty_score=novelty_score, similar_patents=patents)

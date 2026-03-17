"""
PatentGuard IP — TinyFish Client
Wraps HTTP calls to the TinyFish web automation API.
All credentials are loaded from environment variables.
"""

import logging
import os
from typing import TypedDict

import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ── Config (from environment — never hardcoded) ────────────────────────────────
TINYFISH_API_KEY: str = os.getenv("TINYFISH_API_KEY", "")
TINYFISH_WORKFLOW_ID: str = os.getenv("TINYFISH_WORKFLOW_ID", "")
TINYFISH_BASE_URL: str = os.getenv("TINYFISH_BASE_URL", "https://api.tinyfish.io")


# ── Types ──────────────────────────────────────────────────────────────────────
class PatentResult(TypedDict):
    """A single patent result."""
    title: str
    link: str


class TinyFishError(Exception):
    """Raised when the TinyFish API returns an error or unexpected response."""


# ── Client ─────────────────────────────────────────────────────────────────────
async def run_workflow(query: str) -> list[PatentResult]:
    """
    Calls the TinyFish web automation API with the given query.

    :param query: Search query string (invention description).
    :returns: List of PatentResult dicts with title and link.
    :raises TinyFishError: On HTTP error, auth failure, or unexpected response.
    """
    if not TINYFISH_API_KEY or not TINYFISH_WORKFLOW_ID:
        logger.warning(
            "TINYFISH_API_KEY or TINYFISH_WORKFLOW_ID not set. "
            "Returning mock data for development."
        )
        return _mock_results(query)

    headers = {
        "Authorization": f"Bearer {TINYFISH_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    payload = {
        "workflow_id": TINYFISH_WORKFLOW_ID,
        "inputs": {"query": query},
    }

    logger.info("Calling TinyFish workflow %s with query: %s", TINYFISH_WORKFLOW_ID, query[:80])

    async with httpx.AsyncClient(timeout=45.0) as client:
        try:
            response = await client.post(
                f"{TINYFISH_BASE_URL}/v1/workflows/run",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise TinyFishError(
                f"TinyFish HTTP {exc.response.status_code}: {exc.response.text}"
            ) from exc
        except httpx.RequestError as exc:
            raise TinyFishError(f"TinyFish connection error: {exc}") from exc

    data = response.json()

    # Parse TinyFish response — expected: { "results": [{ "title": str, "link": str }] }
    raw_results = data.get("results", [])
    if not isinstance(raw_results, list):
        raise TinyFishError(f"Unexpected TinyFish response format: {data}")

    patents: list[PatentResult] = [
        PatentResult(title=r.get("title", ""), link=r.get("link", ""))
        for r in raw_results
        if r.get("title") and r.get("link")
    ]

    logger.info("TinyFish returned %d patent results.", len(patents))
    return patents


def _mock_results(query: str) -> list[PatentResult]:
    """Return mock patent results for local development when API keys are absent."""
    return [
        PatentResult(
            title="Method and apparatus for automated fluid sterilization using UV-C radiation",
            link="https://patents.google.com/patent/US10123456B2",
        ),
        PatentResult(
            title="Self-decontaminating container with integrated light emitter",
            link="https://patents.google.com/patent/US10987654B1",
        ),
        PatentResult(
            title="Portable water purification device with wireless monitoring",
            link="https://patents.google.com/patent/US11234567A1",
        ),
    ]

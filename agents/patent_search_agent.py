"""
PatentGuard IP — Patent Search Agent
Receives an invention description, calls TinyFish automation workflow,
and returns structured patent data.
"""

import logging
from typing import TypedDict

from services.tinyfish_client import run_workflow, TinyFishError  # noqa: F401 (re-export)

logger = logging.getLogger(__name__)


# ── Types ──────────────────────────────────────────────────────────────────────
class PatentResult(TypedDict):
    """A single patent result returned by the search agent."""
    title: str  # Patent title
    link: str   # URL to patent record


class PatentSearchResponse(TypedDict):
    """Structured response from the Patent Search Agent."""
    patents: list[PatentResult]
    query: str


# ── Agent ──────────────────────────────────────────────────────────────────────
async def search_patents(idea: str) -> PatentSearchResponse:
    """
    Receives an invention description, calls TinyFish automation workflow,
    and returns structured patent data.

    :param idea: Natural language invention description.
    :returns: PatentSearchResponse with list of matching patents.
    :raises TinyFishError: If the TinyFish API call fails.
    """
    logger.info("Patent Search Agent invoked with idea: %s", idea[:80])

    # Delegate web automation to TinyFish
    patents: list[PatentResult] = run_workflow(idea)

    logger.info("Patent Search Agent retrieved %d results.", len(patents))

    return PatentSearchResponse(patents=patents, query=idea)

"""
PatentGuard IP — Novelty Engine
Calculates a novelty score (0–100) for an invention against retrieved patents.
Higher score = more novel (less similar prior art found).
"""

import logging
import math
from typing import TypedDict

logger = logging.getLogger(__name__)


class PatentResult(TypedDict):
    title: str
    link: str


def calculate_novelty_score(idea: str, patents: list[PatentResult]) -> int:
    """
    Calculates a novelty score for the invention against retrieved patents.

    Scoring strategy (MVP):
    - No patents found          → 100 (fully novel)
    - Patents found             → score decreases based on keyword overlap
      between the idea and patent titles.
    - Score range               → 0 (identical prior art) to 100 (fully novel)

    :param idea: Original invention description.
    :param patents: List of similar patents found.
    :returns: Integer score 0–100.
    """
    if not patents:
        logger.info("No patents found — returning max novelty score of 100.")
        return 100

    idea_tokens = _tokenize(idea)
    if not idea_tokens:
        return 50  # Neutral score for empty / non-parseable idea

    total_overlap = 0.0
    for patent in patents:
        patent_tokens = _tokenize(patent.get("title", ""))
        overlap = _jaccard_similarity(idea_tokens, patent_tokens)
        total_overlap += overlap
        logger.debug(
            "Patent '%s' — Jaccard overlap: %.3f",
            patent.get("title", "")[:60],
            overlap,
        )

    # Average similarity across all patents (0.0 – 1.0)
    avg_similarity = total_overlap / len(patents)

    # Apply a logarithmic penalty for number of patents found
    patent_count_penalty = min(1.0, math.log(len(patents) + 1) / math.log(20))

    # Combined similarity factor (weighted 70% avg overlap, 30% count penalty)
    combined = (0.70 * avg_similarity) + (0.30 * patent_count_penalty)

    # Novelty = inverse of similarity, scaled to 0–100
    novelty = max(0, min(100, round((1.0 - combined) * 100)))

    logger.info(
        "Novelty score: %d (avg_similarity=%.3f, count_penalty=%.3f, combined=%.3f)",
        novelty,
        avg_similarity,
        patent_count_penalty,
        combined,
    )
    return novelty


# ── Helpers ────────────────────────────────────────────────────────────────────
_STOP_WORDS = {
    "a", "an", "the", "and", "or", "of", "for", "in", "on", "at",
    "to", "with", "using", "by", "is", "are", "that", "this", "it",
    "as", "from", "be", "was", "were",
}


def _tokenize(text: str) -> set[str]:
    """Lowercase, split, and remove stop words from text."""
    tokens = set(
        word.strip(".,;:()")
        for word in text.lower().split()
        if word.strip(".,;:()") and word.strip(".,;:()") not in _STOP_WORDS
    )
    return tokens


def _jaccard_similarity(set_a: set[str], set_b: set[str]) -> float:
    """Compute Jaccard similarity between two token sets."""
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0

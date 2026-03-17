"""
PatentGuard IP — Patent Search Service (Reliable MVP)
Uses SerpAPI Google Patents search.
"""

import os
from serpapi import GoogleSearch
from dotenv import load_dotenv

load_dotenv()


class TinyFishError(Exception):
    pass


def run_workflow(query: str):

    try:

        params = {
            "engine": "google_patents",
            "q": query,
            "api_key": os.getenv("SERPAPI_KEY")
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        patents = []

        for r in results.get("organic_results", [])[:5]:

            patents.append({
                "title": r.get("title", ""),
                "link": r.get("link", "")
            })

        return patents

    except Exception as e:
        raise TinyFishError(str(e))
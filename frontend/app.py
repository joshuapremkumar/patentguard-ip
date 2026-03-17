"""
PatentGuard IP — Streamlit Frontend
Allows inventors to submit an idea and view novelty analysis results.
"""

import streamlit as st
import httpx
import os

# Backend API URL (defaults to local FastAPI for dev, override via env)
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8080")

st.set_page_config(
    page_title="PatentGuard IP",
    page_icon="🛡️",
    layout="centered",
)

st.title("🛡️ PatentGuard IP")
st.subheader("AI-Powered Patent Novelty Analyzer")
st.markdown(
    "Describe your invention below and let PatentGuard search existing patents "
    "to calculate a **novelty score** and surface similar prior art."
)

st.divider()

# ── Input Section ──────────────────────────────────────────────────────────────
idea = st.text_area(
    label="Invention Description",
    placeholder="e.g. A self-cleaning water bottle that uses UV-C LEDs to sterilize the interior...",
    height=160,
)

analyze_btn = st.button("🔍 Analyze Invention", type="primary", use_container_width=True)

# ── Analysis Section ───────────────────────────────────────────────────────────
if analyze_btn:
    if not idea.strip():
        st.warning("Please enter an invention description before analyzing.")
    else:
        with st.spinner("Searching patents and calculating novelty score…"):
            try:
                response = httpx.post(
                    f"{BACKEND_URL}/analyze",
                    json={"idea": idea.strip()},
                    timeout=60.0,
                )
                response.raise_for_status()
                data = response.json()
            except httpx.HTTPStatusError as exc:
                st.error(f"API error {exc.response.status_code}: {exc.response.text}")
                st.stop()
            except httpx.RequestError as exc:
                st.error(f"Could not reach the backend: {exc}")
                st.stop()

        novelty_score: int = data.get("novelty_score", 0)
        similar_patents: list = data.get("similar_patents", [])

        st.divider()

        # ── Novelty Score ──────────────────────────────────────────────────────
        st.subheader("📊 Novelty Score")
        color = (
            "green" if novelty_score >= 70
            else "orange" if novelty_score >= 40
            else "red"
        )
        st.markdown(
            f"<h1 style='color:{color}; text-align:center;'>{novelty_score} / 100</h1>",
            unsafe_allow_html=True,
        )
        if novelty_score >= 70:
            st.success("✅ High novelty — your invention appears largely unique.")
        elif novelty_score >= 40:
            st.warning("⚠️ Moderate novelty — some similar patents exist.")
        else:
            st.error("❌ Low novelty — closely related patents found.")

        st.progress(novelty_score / 100)

        st.divider()

        # ── Similar Patents ────────────────────────────────────────────────────
        st.subheader("📄 Similar Patents")
        if similar_patents:
            for patent in similar_patents:
                title = patent.get("title", "Unknown Title")
                link = patent.get("link", "#")
                st.markdown(f"- [{title}]({link})")
        else:
            st.info("No similar patents found — your idea may be highly novel!")

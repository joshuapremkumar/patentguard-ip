# 🛡️ PatentGuard IP

**AI-powered patent novelty analyzer** — search patents, detect novelty, and analyze invention similarity using TinyFish web automation agents.

---

## Architecture

```
Inventor (Browser)
      │
      ▼
Streamlit UI (frontend/app.py)
      │  POST /analyze { "idea": "..." }
      ▼
FastAPI Backend (backend/api.py)
      │                │
      ▼                ▼
Patent Search      Novelty Engine
Agent              (services/novelty_engine.py)
(agents/patent_search_agent.py)
      │
      ▼
TinyFish Client (services/tinyfish_client.py)
      │  HTTPS
      ▼
TinyFish Web Automation API
```

---

## Project Structure

```
patentguard-ip/
├── frontend/
│   └── app.py                   # Streamlit UI
├── backend/
│   └── api.py                   # FastAPI — POST /analyze
├── agents/
│   └── patent_search_agent.py   # Patent Search Agent
├── services/
│   ├── tinyfish_client.py       # TinyFish HTTP wrapper
│   └── novelty_engine.py        # Novelty scoring logic
├── deployment/
│   ├── Dockerfile               # Container config (exposes 8080)
│   └── docker-compose.yml       # Local dev orchestration
├── requirements.txt
├── .env.example                 # Environment variable template
└── README.md
```

---

## Quick Start

### 1. Clone & configure

```bash
git clone https://github.com/<your-org>/patentguard-ip.git
cd patentguard-ip
cp .env.example .env
# Edit .env and fill in your TINYFISH_API_KEY and TINYFISH_WORKFLOW_ID
```

### 2. Run locally with Docker Compose

```bash
docker compose -f deployment/docker-compose.yml up --build
```

- **Backend (API):** http://localhost:8080
- **Frontend (UI):** http://localhost:8501

### 3. Run without Docker

```bash
pip install -r requirements.txt

# Terminal 1 — Backend
uvicorn backend.api:app --host 0.0.0.0 --port 8080 --reload

# Terminal 2 — Frontend
BACKEND_URL=http://localhost:8080 streamlit run frontend/app.py
```

---

## API Reference

### `POST /analyze`

**Request:**
```json
{ "idea": "A self-cleaning water bottle using UV-C LEDs..." }
```

**Response:**
```json
{
  "novelty_score": 72,
  "similar_patents": [
    {
      "title": "Method and apparatus for UV-C sterilization of containers",
      "link": "https://patents.google.com/patent/US10123456B2"
    }
  ]
}
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TINYFISH_API_KEY` | Yes | TinyFish API authentication key |
| `TINYFISH_WORKFLOW_ID` | Yes | TinyFish workflow to execute |
| `TINYFISH_BASE_URL` | No | TinyFish base URL (default: `https://api.tinyfish.io`) |
| `BACKEND_URL` | No | FastAPI URL for Streamlit (default: `http://localhost:8080`) |

> ⚠️ **Never commit `.env` to version control.**

---

## Deployment — DigitalOcean App Platform

1. Push this repo to GitHub.
2. Create a new App on DigitalOcean App Platform.
3. Select the GitHub repo and set the **Run Command** to:
   ```
   uvicorn backend.api:app --host 0.0.0.0 --port 8080
   ```
4. Set environment variables (`TINYFISH_API_KEY`, `TINYFISH_WORKFLOW_ID`) in the App settings.
5. Deploy — the platform will build using the `Dockerfile` and expose port 8080.

---

## License

MIT

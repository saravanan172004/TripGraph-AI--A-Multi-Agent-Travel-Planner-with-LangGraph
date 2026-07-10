# ✈️ TripGraph AI — A Multi-Agent Travel Planner with LangGraph

TripGraph AI turns a single natural-language request — *"Plan a 7 day trip to Japan under 2 lakhs"* — into a complete travel plan: flight options, hotel ideas, and a day-by-day itinerary. It's powered by a multi-agent workflow built with **LangGraph**, **LangChain**, and **FastAPI**.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688" alt="FastAPI">
  <img src="https://img.shields.io/badge/LangGraph-Multi--Agent-6E56CF" alt="LangGraph">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="MIT License">
</p>

---

## Why this project?

Planning a trip usually means jumping between flight sites, hotel sites, review blogs, and a spreadsheet to tie it all together. TripGraph AI collapses that into one conversation by coordinating a small team of specialized agents:

- a **flight-research agent**
- a **hotel-research agent**
- an **itinerary-planning agent**
- a **final response agent**

all orchestrated through a LangGraph state machine, so each agent only does the one thing it's good at, then hands off to the next.

---

## Features

- ✈️ Flight research via the AviationStack API
- 🏨 Hotel & sightseeing suggestions via Tavily search
- 🧠 Multi-agent orchestration with LangGraph (stateful, resumable workflow)
- 📝 Structured, markdown-formatted itinerary generation
- 🌐 FastAPI backend with a clean, single-page web interface
- 💾 Conversation state persisted in PostgreSQL (each chat has a `thread_id`, so context carries across turns)
- ⚡ Fast LLM responses via Groq
- 📄 One-click PDF export of the generated plan

---

## Demo

<p align="center">
  <img src="static/demo-screenshot.png" alt="TripGraph AI screenshot" width="800">
</p>



---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| Backend | FastAPI |
| Agent orchestration | LangGraph + LangChain |
| LLM inference | Groq |
| Web search | Tavily API |
| Flight data | AviationStack API |
| Persistence | PostgreSQL |
| Frontend | Jinja2 templates + HTML/CSS/JavaScript |
| Deployment | Docker / Render |

---

## How the Workflow Works

```
User request
     │
     ▼
Flight Agent  ──► gathers flight options (AviationStack)
     │
     ▼
Hotel Agent   ──► searches hotels & sights (Tavily)
     │
     ▼
Itinerary Agent ──► drafts a day-by-day plan
     │
     ▼
Final Agent   ──► formats everything into one polished response
     │
     ▼
Markdown answer + PDF export
```

Each step updates a shared state object; LangGraph handles the transitions and keeps the run resumable via `thread_id`, so a follow-up message continues the same conversation instead of starting over.

---

## Project Structure

```
.
├── app.py                 # FastAPI app entry point
├── backend.py             # LangGraph travel workflow definition
├── requirements.txt       # Python dependencies
├── Dockerfile             # Container build for deployment
├── static/                # CSS, JS, and other static assets
├── templates/             # Jinja2 HTML templates (index.html)
├── tools/                 # Flight & web-search tool integrations
│   ├── flight_tool.py
│   └── tavily_tool.py
├── test.py                # Local test script for the agent workflow
└── .env                   # Local environment variables (not committed)
```

---

## Prerequisites

- Python 3.10 or newer
- PostgreSQL running and accessible
- API keys for:
  - [Groq](https://console.groq.com/)
  - [Tavily](https://tavily.com/)
  - [AviationStack](https://aviationstack.com/)

---

## Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/travel_db
GROQ_API_KEY=your_groq_api_key
AVIATIONSTACK_API_KEY=your_aviationstack_api_key
TAVILY_API_KEY=your_tavily_api_key
DEFAULT_ORIGIN_IATA=DAC
```

> `DEFAULT_ORIGIN_IATA` is the fallback departure airport code used when the user doesn't specify one.

---

## Installation

```bash
git clone https://github.com/saravanan172004/TripGraph-AI--A-Multi-Agent-Travel-Planner-with-LangGraph.git
cd TripGraph-AI--A-Multi-Agent-Travel-Planner-with-LangGraph

python -m venv .venv
source .venv/bin/activate      # On Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

---

## Running Locally

```bash
python app.py
```

Then open your browser at:

```
http://127.0.0.1:8000/
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/api/travel` | Submit a travel request |

Example request:

```bash
curl -X POST http://127.0.0.1:8000/api/travel \
  -H "Content-Type: application/json" \
  -d '{"message":"Plan a 3-day trip to Tokyo with a budget of $1200"}'
```

Response:

```json
{
  "success": true,
  "answer": "## Your 3-Day Tokyo Itinerary\n...",
  "thread_id": "generated-thread-id"
}
```

---

## Deployment

The project includes a `Dockerfile`, so it can be deployed anywhere that runs containers (Render, Railway, Fly.io, etc.).

**Render (free/hobby tier) quick setup:**

- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn app:app --host 0.0.0.0 --port $PORT`
- Add all four environment variables above (plus `DATABASE_URL` pointing to a managed Postgres instance) under the Render dashboard's *Environment* tab.

---

## Contributing

Contributions are welcome:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Open a pull request

---

## License

Distributed under the MIT License. See [`LICENSE`](./LICENSE) for details.

---

## Acknowledgments

Built with LangGraph, LangChain, FastAPI, Groq, Tavily, and AviationStack — and inspired by the broader open-source LangGraph travel-planner community.

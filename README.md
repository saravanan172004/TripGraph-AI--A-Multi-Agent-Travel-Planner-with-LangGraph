# ✈️ TripGraph AI — A Multi-Agent Travel Planner with LangGraph & MCP

TripGraph AI turns a single natural-language request — *"Plan a 7 day trip to Japan under 2 lakhs"* — into a complete travel plan: flight options, hotel ideas, live weather, and a day-by-day itinerary. It's powered by a fully async, multi-agent workflow built with **LangGraph**, **LangChain**, **FastAPI**, and the **Model Context Protocol (MCP)**.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688" alt="FastAPI">
  <img src="https://img.shields.io/badge/LangGraph-Multi--Agent-6E56CF" alt="LangGraph">
  <img src="https://img.shields.io/badge/MCP-Tool%20Servers-orange" alt="MCP">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="MIT License">
</p>

<p align="center">
  <a href="https://tripgraph-ai-a-multi-agent-travel.onrender.com">🔗 Live Demo</a>
</p>

---

## Why this project?

Planning a trip usually means jumping between flight sites, hotel sites, weather apps, and a spreadsheet to tie it all together. TripGraph AI collapses that into one conversation by coordinating a small team of specialized agents:

- a **flight-research agent** — airport & airline data via an Aviationstack MCP server
- a **hotel-research agent** — live web search via a Tavily MCP server
- a **weather agent** — current conditions & forecast via a custom OpenWeatherMap MCP server
- an **itinerary-planning agent** — drafts the day-by-day plan
- a **final response agent** — formats everything into one polished answer

All five run as nodes in a LangGraph state machine, each doing one job well and handing off state to the next.

---

## Features

- ✈️ Flight & airport/airline data via an **Aviationstack MCP server**
- 🏨 Hotel & sightseeing suggestions via a **Tavily MCP server**
- 🌦️ Live current weather + forecast via a **custom OpenWeatherMap MCP server** (`custom_weather_mcp_server.py`)
- 🔌 **MCP-based tool architecture** — all external data sources are pluggable MCP servers, wired together with a single `MultiServerMCPClient`
- 🧠 Multi-agent orchestration with LangGraph (stateful, resumable workflow)
- ⚙️ Fully **async pipeline end-to-end** — `ainvoke`, async agents, async Postgres checkpointing, no nested event loops
- 📝 Structured, markdown-formatted itinerary generation
- 🌐 FastAPI backend with a clean, single-page web interface
- 💾 Conversation state persisted in PostgreSQL via `AsyncPostgresSaver` (each chat has a `thread_id`, so context carries across turns)
- ⚡ Fast LLM responses via Groq
- 📄 One-click PDF export of the generated plan
- 🐳 Dockerized, deployed on Render

---

## Demo

<p align="center">
  <img src="static/demo-screenshot.png" alt="TripGraph AI screenshot" width="800">
</p>

Live: **[tripgraph-ai-a-multi-agent-travel.onrender.com](https://tripgraph-ai-a-multi-agent-travel.onrender.com)**

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| Backend | FastAPI (fully async) |
| Agent orchestration | LangGraph + LangChain |
| Tool integration | Model Context Protocol (MCP) via `langchain-mcp-adapters` |
| LLM inference | Groq |
| Web search | Tavily MCP server (streamable HTTP) |
| Flight data | Aviationstack MCP server (stdio, via `uvx`) |
| Weather data | Custom MCP server over the OpenWeatherMap API (stdio) |
| Persistence | PostgreSQL (`AsyncPostgresSaver`) |
| Frontend | Jinja2 templates + HTML/CSS/JavaScript |
| Deployment | Docker + Render |

---

## MCP Architecture

Instead of calling third-party APIs directly, every external data source is exposed as an **MCP tool server**, and the backend talks to all of them through one `MultiServerMCPClient`:

```
                    ┌──────────────────────────────┐
                    │      MultiServerMCPClient      │
                    └───────────────┬────────────────┘
           ┌────────────────────────┼───────────────────────┐
           ▼                        ▼                        ▼
 ┌───────────────────┐   ┌────────────────────┐   ┌───────────────────────┐
 │   Tavily MCP        │   │  Aviationstack MCP  │   │  Custom Weather MCP    │
 │  (streamable_http)  │   │  (stdio, via uvx)   │   │  (stdio, our script)   │
 │  tavily_search       │   │  list_airports       │   │  get_current_weather    │
 │                      │   │  list_airlines       │   │  get_forecast           │
 └───────────────────┘   └────────────────────┘   └───────────────────────┘
```

`mcp_client.py` fetches the full tool list **once** and caches it (`get_cached_tools()`), rather than reconnecting to every server on every request — each agent just looks up the tool it needs (`tavily_search`, `list_airports`, `get_current_weather`, etc.) from that shared cache.

---

## How the Workflow Works

```
User request
     │
     ▼
Flight Agent    ──► airport & airline data (Aviationstack MCP)
     │
     ▼
Hotel Agent     ──► hotel & sightseeing search (Tavily MCP)
     │
     ▼
Weather Agent   ──► current weather + forecast (Custom Weather MCP)
     │
     ▼
Itinerary Agent ──► drafts a day-by-day plan
     │
     ▼
Final Agent     ──► formats everything into one polished response
     │
     ▼
Markdown answer + PDF export
```

Each step updates a shared state object; LangGraph handles the transitions asynchronously (`ainvoke`) and keeps the run resumable via `thread_id`, so a follow-up message continues the same conversation instead of starting over.

---

## Project Structure

```
.
├── app.py                        # FastAPI app entry point
├── backend.py                    # LangGraph travel workflow (agents + graph)
├── mcp_client.py                 # MultiServerMCPClient + shared tool cache
├── custom_weather_mcp_server.py  # Custom MCP server wrapping OpenWeatherMap
├── requirements.txt              # Python dependencies
├── DockerFile                    # Container build for deployment
├── static/                       # CSS, JS, favicon, and other static assets
├── templates/                    # Jinja2 HTML templates (index.html)
├── tools/                        # Legacy direct-API tools (superseded by MCP servers)
│   ├── flight_tool.py
│   └── tavily_tool.py
├── test.py                       # Local test script for the agent workflow
├── mcp_client_test.py            # Local test script for MCP tool connectivity
└── .env                          # Local environment variables (not committed)
```

---

## Prerequisites

- Python 3.10 or newer
- [`uv`](https://docs.astral.sh/uv/) installed locally (provides `uvx`, used to launch the Aviationstack MCP server)
- PostgreSQL running and accessible
- API keys for:
  - [Groq](https://console.groq.com/)
  - [Tavily](https://tavily.com/)
  - [AviationStack](https://aviationstack.com/)
  - [OpenWeatherMap](https://openweathermap.org/api)

---

## Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/travel_db
GROQ_API_KEY=your_groq_api_key
AVIATIONSTACK_API_KEY=your_aviationstack_api_key
TAVILY_API_KEY=your_tavily_api_key
OPENWEATHER_API_KEY=your_openweathermap_api_key
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
  "thread_id": "generated-thread-id",
  "flight_results": "...",
  "hotel_results": "...",
  "itinerary": "...",
  "llm_calls": 5
}
```

---

## Deployment

Live at: **[tripgraph-ai-a-multi-agent-travel.onrender.com](https://tripgraph-ai-a-multi-agent-travel.onrender.com)**

The project ships with a `DockerFile`, so it can be deployed anywhere that runs containers (Render, Railway, Fly.io, etc.). The image installs `uv` so the Aviationstack MCP server (launched via `uvx`) can actually start inside the container — this is required, not optional.

**Render (free/hobby tier) quick setup:**

- **Environment:** Docker (uses the repo's `DockerFile`)
- **Start Command:** already set via `CMD` in the `DockerFile` (`uvicorn app:app --host 0.0.0.0 --port 8000`)
- Add all five environment variables from above (`GROQ_API_KEY`, `TAVILY_API_KEY`, `AVIATIONSTACK_API_KEY`, `OPENWEATHER_API_KEY`, `DATABASE_URL`, `DEFAULT_ORIGIN_IATA`) under the Render dashboard's **Environment** tab — they don't carry over from your local `.env`, they have to be entered there directly.

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

Built with LangGraph, LangChain, the Model Context Protocol, FastAPI, Groq, Tavily, AviationStack, and OpenWeatherMap — and inspired by the broader open-source LangGraph travel-planner community.
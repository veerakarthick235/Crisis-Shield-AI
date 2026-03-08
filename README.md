# 🛡️ CrisisShield AI

**Autonomous Multi-Agent Disaster Detection & Response Coordination System**

Built with FastAPI, Fetch.ai uAgents architecture, and a real-time HTML/CSS/JS dashboard.

---

## Quick Start

```bash
# 1. Install dependencies
cd backend
pip install -r requirements.txt

# 2. Start the server (launches all 5 agents + API + dashboard)
python main.py
```

Open **http://localhost:8000** to view the dashboard.
API docs at **http://localhost:8000/docs**.

---

## Architecture

```
SignalWatch Agent → RiskPredict Agent → CitizenAlert Agent
                                      → RescueCoordinator Agent
                                      → ResourceSupply Agent
```

All agents run as concurrent async tasks within a single FastAPI process, communicating via a thread-safe shared state bus.

## Project Structure

```
crystal-mariner/
├── backend/           # FastAPI + Agent system
│   ├── agents/        # 5 autonomous agents
│   ├── models/        # Pydantic data models
│   ├── routes/        # API endpoints
│   ├── services/      # Data simulator + agent bridge
│   └── main.py        # Entry point
├── frontend/          # Dashboard UI
│   ├── css/           # Premium dark theme
│   ├── js/            # App logic + charts
│   └── index.html     # Main page
└── docs/              # Project documentation
    └── PROJECT_DOCUMENT.md
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI, Uvicorn |
| Agent Framework | Fetch.ai uAgents pattern |
| Frontend | HTML5, CSS3, JavaScript |
| Data | Simulated environmental sources |

---

*CrisisShield AI — Because every minute of warning saves lives.*

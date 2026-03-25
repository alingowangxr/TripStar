# GEMINI.md - TripStar (旅途星辰)

This document provides context and guidelines for working with the **TripStar** project, an AI-powered travel planning platform built on the **HelloAgents** framework.

## Project Overview

**TripStar** is a multi-agent collaborative travel planning system designed to solve information overload for travelers. It uses Large Language Models (LLMs) to automatically search for attractions, weather, and hotels to generate personalized itineraries.

### Core Technology Stack
- **Frontend**: Vue 3 (Composition API), TypeScript, Vite, Ant Design Vue, ECharts (for knowledge graphs), AMap JS API 2.0 (interactive maps).
- **Backend**: Python 3.10+, FastAPI, Uvicorn, Pydantic (data validation).
- **AI/Agents**: 
    - **HelloAgents**: Framework for multi-agent orchestration.
    - **Model Context Protocol (MCP)**: Used via `fastmcp` to connect to AMap services.
    - **LLM**: Compatible with OpenAI-style APIs (e.g., Doubao, Qwen).
- **External APIs**: AMap (Maps/POI), Unsplash (Images).

### Architecture
- **Agentic Workflow**: Uses specialized agents (Attraction, Weather, Hotel, Planner) that collaborate to produce a structured trip plan.
- **Asynchronous Task Polling**: Long-running LLM tasks are handled via a task ID system (`POST /api/trip/plan` -> `GET /api/trip/status/{task_id}`) to prevent gateway timeouts.
- **Frontend-Backend Separation**: The frontend communicates with the FastAPI backend via Axios.

---

## Building and Running

### Backend Setup
1.  **Environment**: Python 3.10+ and `uv` package manager (optional but recommended).
2.  **Installation**:
    ```bash
    cd backend
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```
3.  **Configuration**: Copy `backend/.env.example` to `backend/.env` and fill in:
    - `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL_ID`
    - `VITE_AMAP_WEB_KEY` (AMap Web Service Key)
    - `UNSPLASH_ACCESS_KEY`
4.  **Running**:
    ```bash
    uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload
    ```

### Frontend Setup
1.  **Environment**: Node.js 18+.
2.  **Installation**:
    ```bash
    cd frontend
    npm install
    ```
3.  **Configuration**: Copy `frontend/.env.example` to `frontend/.env` and fill in:
    - `VITE_AMAP_WEB_KEY` (Same as backend)
    - `VITE_AMAP_WEB_JS_KEY` (AMap JS API Key)
    - **Security**: Inject `securityJsCode` in `index.html` for AMap 2.0.
4.  **Running**:
    ```bash
    npm run dev
    ```

---

## Development Conventions

### Agent Definitions
Agents are defined in `backend/app/agents/trip_planner_agent.py`. 
- **System Prompts**: Contain strict tool-calling formats (e.g., `[TOOL_CALL:...]`).
- **Tools**: Integrated via MCP (e.g., `amap-mcp-server`).
- **Logic**: The `MultiAgentTripPlanner` class coordinates the execution flow, currently optimizing steps 1-3 to run sequentially (to avoid resource contention) followed by a final planning step.

### API & Schemas
- **Models**: Defined in `backend/app/models/schemas.py`. Use Pydantic models for structured LLM output and API responses.
- **Routes**: Located in `backend/app/api/routes/`. 
    - `trip.py`: Handles plan generation and task status polling.
    - `chat.py`: Handles contextual AI chat after a plan is generated.

### Frontend Patterns
- **Services**: `frontend/src/services/api.ts` manages API calls. `generateTripPlan` implements the polling logic.
- **I18n**: Multi-language support is managed in `frontend/src/i18n/`.
- **Styling**: Uses Sass and a custom "Dark Luxury Glassmorphism" theme.

### Testing & Validation
- **Manual Verification**: Test new agent capabilities by triggering a trip plan and monitoring the terminal for tool-call execution.
- **API Docs**: Access Swagger UI at `http://localhost:8000/docs`.

---

## Key Files
- `backend/app/agents/trip_planner_agent.py`: The "brain" of the system.
- `backend/app/api/routes/trip.py`: Task scheduling and status management.
- `frontend/src/views/Result.vue`: Main display logic for generated itineraries.
- `frontend/src/services/api.ts`: Frontend polling and API client.

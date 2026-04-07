# MailPilot Command Center

AI-powered email triage platform built for the Meta OpenEnv Hackathon. MailPilot helps teams prioritize, classify, and resolve support inboxes faster with AI-assisted triage, urgency scoring, and a unique Focus Sprint mode for high-impact execution.

## Why this project

Support teams lose time manually sorting inboxes while urgent customer issues get buried. MailPilot turns unstructured email streams into an actionable command center with:

- AI-generated summaries and suggested replies
- Real-time urgency scoring and smart prioritization
- Focus Sprint mode to maximize high-impact resolution in short windows
- Dashboard KPIs for leadership visibility

## Core Features

- Smart inbox queue ranked by urgency
- AI triage endpoint with OpenAI + deterministic fallback heuristics
- Status workflow: new -> in_progress -> resolved -> archived
- KPI dashboard and category analytics
- Focus Sprint (unique feature): one-click high-impact queue generation and projected impact score
- Responsive UI with modern visual design

## Tech Stack

- Frontend: React + Vite
- Backend: Node.js + Express
- Database: MongoDB + Mongoose
- AI: OpenAI Responses API with heuristic fallback

## Architecture

```text
React UI (Vite)
   |
   v
Express API (REST)
   |- /api/emails/*        -> CRUD + triage actions
   |- /api/insights/*      -> KPIs + Focus Sprint
   |
   v
MongoDB (Email documents + indexes)
   |
   v
AI Service
   |- OpenAI model (if key exists)
   |- Heuristic triage fallback (always available)
```

## Folder Structure

```text
hackathon-meta-mailpilot/
  backend/
    src/
      config/
      controllers/
      middleware/
      models/
      routes/
      services/
      utils/
  frontend/
    src/
      api/
      components/
      App.jsx
      main.jsx
      styles.css
  .env.example
  .gitignore
  README.md
```

## Setup

### Prerequisites

- Node.js 20+
- npm 10+
- MongoDB 7+ (if running locally without Docker)
- Optional: OpenAI API key for live AI triage

### Option A: One-command run with Docker Compose (recommended for judges)

```bash
docker compose up --build
```

Then open:

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:5000/api/health`

### Option B: Local development run

### 1) Backend

```bash
cd backend
cp .env.example .env
npm install
npm run dev
```

In a second terminal, seed sample data:

```bash
cd backend
npm run seed
```

### 2) Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Frontend runs on `http://localhost:5173` and backend on `http://localhost:5000`.

## Health Check

After starting the backend:

```bash
curl http://localhost:5000/api/health
```

Expected response:

```json
{ "status": "ok", "service": "mailpilot-api" }
```

## API Documentation

### Health

- `GET /api/health`

### Emails

- `GET /api/emails` - list emails
- `GET /api/emails/:id` - get single email
- `POST /api/emails` - create email
- `PATCH /api/emails/:id/status` - update status
- `POST /api/emails/:id/triage` - run AI triage

### Insights

- `GET /api/insights/dashboard` - dashboard KPIs
- `POST /api/insights/focus-sprint` - build sprint queue

## Demo Script (2-3 mins)

1. Open dashboard and show KPI cards + urgency-ranked queue.
2. Select a critical email and click **Run AI Triage**.
3. Show generated summary, suggested reply, and updated priority/category/sentiment.
4. Click **Launch 15m Sprint** to show projected impact and curated action queue.
5. Resolve one email and show KPI changes in real-time.

## Future Improvements

- Team-level assignment and SLA breach alerts
- OAuth + RBAC for enterprise accounts
- RAG over support docs for grounded AI replies
- WebSocket live inbox updates
- Multi-tenant analytics and customer retention prediction

## Troubleshooting

- `MongooseServerSelectionError`: start MongoDB locally or run `docker compose up --build`.
- CORS issues: ensure `FRONTEND_URL` in backend `.env` matches your frontend origin.
- AI triage not using OpenAI: set `OPENAI_API_KEY` in backend `.env`; fallback heuristics still work without it.

# SentinelMesh Production Deployment Guide

This guide details the complete production deployment architecture and step-by-step instructions for deploying **SentinelMesh — Intelligent Multi-Agent Framework for Automated Software Testing and Bug Analysis**.

---

## 1. Architecture Overview

SentinelMesh combines an interactive React 19 Single Page Application (SPA) with a high-throughput Python FastAPI backend orchestrating an autonomous swarm of 9 specialized QA agents.

```
+---------------------------------------------------------------------------------------+
|                                    CLIENT BROWSER                                     |
|                       React 19 + Vite 8 + Tailwind CSS v4 Dashboard                   |
+---------------------------------------------------------------------------------------+
                    |                                                ^
         REST API (HTTP/HTTPS)                        Live Telemetry Stream (WSS/WS)
         Endpoints: /api/runs, /api/projects          Endpoint: /ws/runs/{run_id}
                    v                                                |
+---------------------------------------------------------------------------------------+
|                            FASTAPI PRODUCTION BACKEND                                 |
|                                                                                       |
|   +-------------------------------------------------------------------------------+   |
|   | Global Security & Telemetry Middleware                                        |   |
|   | - CSP, HSTS, X-Content-Type-Options: nosniff, X-Frame-Options: SAMEORIGIN     |   |
|   | - In-memory Token-Bucket Rate Limiter (600 req/min per IP)                    |   |
|   | - Distributed Trace Propagation (X-Trace-ID)                                  |   |
|   +-------------------------------------------------------------------------------+   |
|                                                                                       |
|   +-------------------------------------------------------------------------------+   |
|   | Autonomous 9-Agent Swarm Execution Engine                                     |   |
|   | Orchestrator -> StaticAnalysis -> TestGen -> TestRunner -> Coverage           |   |
|   |              -> Mutation -> Classifier -> AutoFix -> Verifier (Critic Debate) |   |
|   +-------------------------------------------------------------------------------+   |
|                                                                                       |
|   +-------------------------------------------------------------------------------+   |
|   | Subprocess Sandbox Runner (CPU/Memory/Timeout Caps, Sanitized Host Env)       |   |
|   +-------------------------------------------------------------------------------+   |
+---------------------------------------------------------------------------------------+
             |                                                       |
             v                                                       v
+--------------------------+                               +--------------------------+
|  PERSISTENT DATA VOLUME  |                               |    STORAGE REPOSITORY    |
|  SQLite (WAL mode) /     |                               |  Uploaded Code Archives  |
|  Managed PostgreSQL      |                               |  Generated Audit Reports |
|  Path: /app/data/*.db    |                               |  Path: /app/data/projects|
+--------------------------+                               +--------------------------+
```

---

## 2. Choosing the Right Deployment Strategy

| Strategy | Frontend | Backend | Best For | Persistent Disk | WebSockets |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **Option A (Recommended)** | Unified Container | Render / Railway / VPS | Production, Zero CORS, Single URL | Yes | Full native support |
| **Option B (Decoupled)** | Vercel (Edge) | Render / Railway | Teams with existing Vercel workflows | Backend only | Handled by backend |
| **Option C (Self-Hosted)** | Docker Compose | Ubuntu / Debian VPS | Full infrastructure control, air-gapped | Yes | Local / Nginx proxy |

> [!IMPORTANT]
> **Why the Backend Cannot Run Purely on Serverless (e.g. Vercel Functions):**
> SentinelMesh executes long-running multi-agent pipelines (5–60s) using background `asyncio` tasks, bidirectional WebSocket telemetry (`/ws/runs/...`), and isolated subprocesses for mutation and syntax testing. Serverless functions terminate prematurely and do not support continuous WebSocket streaming.

---

## 3. Production Environment Variables

Configure these environment variables in your hosting provider's dashboard:

| Variable | Required | Default | Description |
| :--- | :---: | :---: | :--- |
| `PORT` | Auto | `8000` | Port assigned dynamically by Render/Railway/Docker. |
| `HOST` | No | `0.0.0.0` | Bind interface. Always `0.0.0.0` inside containers. |
| `CORS_ORIGINS` | No | `*` | Comma-separated list of allowed origins (e.g. `https://sentinelmesh.vercel.app`). |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity (`INFO`, `DEBUG`, `WARNING`, `ERROR`). |
| `DATA_DIR` | No | `/app/data` | Directory where database and project uploads persist. |
| `SENTINEL_DATABASE_URL` | No | `sqlite:////app/data/sentinelmesh.db` | SQLite or PostgreSQL connection string. |
| `DATABASE_URL` | No | *(None)* | Standard cloud PostgreSQL URL (e.g. from Render/Railway). |
| `GEMINI_API_KEY` | Optional | *(None)* | Google Gemini key for LLM-powered test generation. |
| `OPENAI_API_KEY` | Optional | *(None)* | OpenAI key for LLM-powered test generation. |
| `OLLAMA_BASE_URL` | Optional | *(None)* | Local Ollama endpoint if using private self-hosted models. |
| `VITE_API_URL` | Frontend only | *(Origin)* | Backend API URL (only needed when frontend is on Vercel). |
| `VITE_WS_URL` | Frontend only | *(Origin)* | Backend WebSocket URL (only needed when frontend is on Vercel). |

---

## 4. Option A: Deploying on Render (Recommended Unified Setup)

Render provides Docker runtime support, persistent disk volumes, automatic HTTPS, and native WebSocket streaming.

### Step 1: Connect GitHub Repository
1. Log in to [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** -> **Web Service**.
3. Connect your repository: `https://github.com/HARIESHPERIASAMY/S5_Mini_Project`.
4. Select the branch: `ui-v2` (or `main` if merged).

### Step 2: Configure Service Settings
- **Name**: `sentinelmesh`
- **Region**: Choose the region closest to you (e.g. `Oregon (US West)` or `Frankfurt (EU)`).
- **Environment**: `Docker`
- **Dockerfile Path**: `Dockerfile`
- **Instance Type**: `Starter` (0.5 CPU, 512MB RAM minimum; 1 CPU / 2GB RAM recommended).

### Step 3: Attach Persistent Disk (Critical for Data Persistence)
1. Scroll down to **Disks** and click **Add Disk**.
2. **Name**: `sentinelmesh-data`
3. **Mount Path**: `/app/data`
4. **Size**: `5 GB` (sufficient for ~500 runs and project uploads).

### Step 4: Add Environment Variables
Under the **Environment Variables** tab, add:
- `CORS_ORIGINS`: `*`
- `DATA_DIR`: `/app/data`
- `LOG_LEVEL`: `INFO`
- *(Optional)* `GEMINI_API_KEY` or `OPENAI_API_KEY`

### Step 5: Health Check
- **Health Check Path**: `/healthz`

Click **Create Web Service**. Render will automatically build the multi-stage Docker container and deploy your live URL (e.g., `https://sentinelmesh.onrender.com`).

---

## 5. Option B: Deploying on Railway

Railway supports instant Docker deployment with zero configuration and persistent volumes.

1. Go to [Railway.app](https://railway.app/) and create a new project.
2. Select **Deploy from GitHub repo** and pick `HARIESHPERIASAMY/S5_Mini_Project`.
3. In **Settings**:
   - **Build**: Railway automatically detects the root `Dockerfile`.
   - **Healthcheck Path**: `/healthz`
4. In **Volumes**:
   - Click **Add Volume**.
   - Set **Mount Path**: `/app/data`.
5. Under **Variables**:
   - `CORS_ORIGINS`: `*`
   - `DATA_DIR`: `/app/data`
6. Click **Generate Domain** under **Networking** to receive your public production HTTPS URL.

---

## 6. Option C: Decoupled Setup (Vercel Frontend + Cloud Backend)

If you prefer hosting the React dashboard on Vercel's global CDN:

### Part 1: Deploy Backend (Render / Railway / VPS)
Follow Option A or B above to get your public backend URL, e.g.:
`https://sentinelmesh-api.onrender.com`

### Part 2: Deploy Frontend on Vercel
1. Go to [Vercel](https://vercel.com/) and click **Add New Project**.
2. Import `HARIESHPERIASAMY/S5_Mini_Project`.
3. Configure the Project:
   - **Root Directory**: `frontend`
   - **Framework Preset**: `Vite`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Set Environment Variables:
   - `VITE_API_URL`: `https://sentinelmesh-api.onrender.com`
   - `VITE_WS_URL`: `wss://sentinelmesh-api.onrender.com`
5. Click **Deploy**. Vercel will build and assign your production frontend URL (e.g. `https://sentinelmesh.vercel.app`).
6. Update the backend `CORS_ORIGINS` variable on Render/Railway to include your Vercel domain:
   `CORS_ORIGINS=https://sentinelmesh.vercel.app`

---

## 7. Option D: Self-Hosted Docker Deployment (VPS / EC2)

Deploy directly to an Ubuntu or Debian server using Docker and Docker Compose.

```bash
# 1. Clone repository
git clone https://github.com/HARIESHPERIASAMY/S5_Mini_Project.git
cd S5_Mini_Project

# 2. Build and start services in background
docker compose up -d --build

# 3. Check health and container status
docker compose ps
curl http://localhost:8000/healthz

# 4. View real-time logs
docker compose logs -f
```

---

## 8. Post-Deployment Verification Checklist

Once deployed, run through this smoke-test checklist against your production URL:

- [ ] **Liveness Probe**: `GET https://<your-domain>/healthz` returns `{"status": "healthy"}`.
- [ ] **Readiness Probe**: `GET https://<your-domain>/readyz` returns `{"status": "ready", "database": "connected"}`.
- [ ] **SPA Route Refresh**: Open `https://<your-domain>/overview` and press `F5`. The page loads without 404 errors.
- [ ] **Demo Run Execution**: Click **Analyze code** -> **Launch Demo Run**. The 9-agent pipeline executes.
- [ ] **Live Telemetry Stream**: The status bar in the bottom left displays `● Backend connected` and updates stream over WebSocket.
- [ ] **Findings Inspection**: Click into any detected defect to view the causal chain, file context, and unified diff patch.
- [ ] **Patch Export**: Click **Export** -> **PR patch (.patch)**. The unified diff downloads correctly.
- [ ] **Grounded Assistant**: Open the **Mesh Assistant** drawer on the right and ask:
  *"Which tests failed in this run?"*
  Confirm it replies grounded in the run's real telemetry with citation chips.
- [ ] **Persistence Across Redeploys**: Check the **Run history** view to confirm historical runs persist after redeploying.

---

## 9. Monitoring & Production Logs

- **Render**: Open your Web Service -> Click **Logs** tab in the sidebar.
- **Railway**: Click the service container -> Click **Deploy Logs** or **Runtime Logs**.
- **Docker**: Run `docker logs -f sentinelmesh_app`.
- **System Metrics Endpoint**: `GET /api/metrics` displays live requests, latency distribution, and active agent execution counts.

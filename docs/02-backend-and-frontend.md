# 📘 PART 2 — Backend & Frontend Code Walkthrough
### Quick-Task Hub | DevOps Final Exam | FA23-BCS-201

---

## ⚙️ BACKEND — Node.js / Express API

The backend is the brain of the app. It receives HTTP requests from the frontend, validates data, communicates with MongoDB, and returns responses.

---

### 📄 `backend/package.json` — Dependency Manifest

```json
{
  "name": "quick-task-hub",
  "version": "1.0.0",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "cors": "^2.8.5",
    "dotenv": "^16.3.1",
    "express": "^4.18.2",
    "mongoose": "^8.0.0"
  }
}
```

**Every dependency explained:**

| Package | Purpose |
|---|---|
| `express` | Web server framework. Handles routing (`GET /api/tasks`), middleware, and HTTP responses |
| `mongoose` | MongoDB Object Document Mapper. Lets us define schemas and query MongoDB using JS objects instead of raw queries |
| `cors` | Cross-Origin Resource Sharing middleware — allows the browser/frontend to make requests to the backend safely |
| `dotenv` | Loads environment variables from `.env` file (like `MONGO_URI`, `PORT`) into `process.env` at runtime |

---

### 📄 `backend/server.js` — Application Entry Point

```js
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const path = require('path');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;
```
> **`process.env.PORT || 3000`** — In Docker/K8s, `PORT` is injected as an environment variable. Locally, it defaults to 3000 if no env var is set.

```js
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '../frontend')));
```
> **Three middleware layers registered:**
> - `cors()` — allows cross-origin HTTP requests (browser talking to backend)
> - `express.json()` — parses incoming request bodies as JSON automatically
> - `express.static()` — serves frontend HTML/CSS/JS files directly from the backend (fallback mode)

```js
const MONGO_URI = process.env.MONGO_URI || 'mongodb://localhost:27017/taskdb';
mongoose.connect(MONGO_URI)
  .then(() => console.log('✅ Connected to MongoDB'))
  .catch(err => console.error('❌ MongoDB connection error:', err));
```
> **`process.env.MONGO_URI`** is different in each environment:
> - **Docker Compose:** `mongodb://mongo:27017/taskdb` (uses Docker service name `mongo`)
> - **Kubernetes:** `mongodb://mongo-service:27017/taskdb` (uses K8s Service name `mongo-service`)
> - **Local dev:** `mongodb://localhost:27017/taskdb` (direct connection)

```js
const taskRoutes = require('./routes/tasks');
app.use('/api/tasks', taskRoutes);

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', db: mongoose.connection.readyState === 1 ? 'connected' : 'disconnected' });
});
```
> **`/api/health`** is the critical health-check endpoint. It reports:
> - `status: 'ok'` — always true if server is running
> - `db: 'connected'` — true only if Mongoose successfully connected to MongoDB (`readyState === 1`)
>
> This endpoint is used by Docker Compose health checks, Kubernetes readiness probes, and the Selenium test suite.

```js
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '../frontend/index.html'));
});

app.listen(PORT, () => {
  console.log(`🚀 Quick-Task Hub running on http://localhost:${PORT}`);
});
```
> The `*` wildcard catches any unmatched routes and serves the frontend `index.html` — this enables SPA (Single Page Application) routing.

---

### 📄 `backend/routes/tasks.js` — CRUD API Endpoints

This file defines the **Mongoose schema** (the data model) and all **REST API routes**.

#### The Task Schema (Data Model)

```js
const taskSchema = new mongoose.Schema({
  title:       { type: String, required: true, trim: true },
  description: { type: String, trim: true, default: '' },
  priority:    { type: String, enum: ['low', 'medium', 'high'], default: 'medium' },
  status:      { type: String, enum: ['pending', 'in-progress', 'completed'], default: 'pending' },
  dueDate:     { type: Date },
  createdAt:   { type: Date, default: Date.now }
});
```

**Schema field breakdown:**

| Field | Type | Validation | Default |
|---|---|---|---|
| `title` | String | Required, whitespace trimmed | — |
| `description` | String | Optional, trimmed | `''` |
| `priority` | String | Must be `low`, `medium`, or `high` | `medium` |
| `status` | String | Must be `pending`, `in-progress`, or `completed` | `pending` |
| `dueDate` | Date | Optional | — |
| `createdAt` | Date | Auto-set on creation | `Date.now` |

Mongoose enforces these rules automatically. If you POST a task with `priority: 'urgent'`, it rejects it with a `400 Bad Request`.

#### API Endpoints Summary

| Method | Route | Handler | Description |
|---|---|---|---|
| `GET` | `/api/tasks` | `Task.find(filter)` | Fetch all tasks. Supports `?status=` and `?priority=` query params |
| `GET` | `/api/tasks/:id` | `Task.findById(id)` | Fetch a single task by MongoDB `_id` |
| `POST` | `/api/tasks` | `new Task(body).save()` | Create a new task |
| `PATCH` | `/api/tasks/:id` | `Task.findByIdAndUpdate()` | Partially update a task |
| `DELETE` | `/api/tasks/:id` | `Task.findByIdAndDelete()` | Delete a task |

#### Filter Query Parameters

The `GET /api/tasks` route supports filtering:
```js
const { status, priority } = req.query;
const filter = {};
if (status)   filter.status   = status;
if (priority) filter.priority = priority;
const tasks = await Task.find(filter).sort({ createdAt: -1 });
```
This means you can do:
- `GET /api/tasks?status=pending` — only pending tasks
- `GET /api/tasks?priority=high` — only high priority tasks
- `GET /api/tasks?status=pending&priority=high` — both filters combined

---

## 🌐 FRONTEND — Nginx + Single Page App

The frontend is a single-file application (`index.html`) that contains all the HTML structure, CSS styling, and JavaScript logic. Nginx serves this file and also acts as a reverse proxy to forward API calls to the backend.

---

### 📄 `frontend/nginx.conf` — The Web Server Configuration

```nginx
server {
    listen 80;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    # Serve static frontend files
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy API requests to the backend container
    location /api/ {
        proxy_pass         http://app:3000/api/;
        proxy_http_version 1.1;
        proxy_set_header   Upgrade $http_upgrade;
        proxy_set_header   Connection 'upgrade';
        proxy_set_header   Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
}
```

**Line-by-line explanation:**

| Line | Meaning |
|---|---|
| `listen 80` | Nginx listens on port 80 (standard HTTP) |
| `server_name _` | Accepts requests from any hostname/IP |
| `root /usr/share/nginx/html` | This is where the static files live inside the container |
| `try_files $uri $uri/ /index.html` | Try to serve the exact file, then directory, then fall back to `index.html` (needed for SPA routing) |
| `location /api/` | Any request URL starting with `/api/` gets forwarded (proxied) |
| `proxy_pass http://app:3000/api/` | Forward to the backend container named `app` on port 3000 — `app` is the **Docker Compose service name** and **Kubernetes Service name** |
| `proxy_http_version 1.1` | Use HTTP 1.1 to support WebSocket upgrades |
| `proxy_set_header Host $host` | Pass the original Host header to the backend |
| `gzip on` | Compress responses to reduce bandwidth usage |

> **Why is the backend address `app:3000`?**
> In Docker Compose, the backend service is named `app`. Docker's internal DNS resolves the service name `app` to the container's internal IP automatically. In Kubernetes, the ClusterIP Service is also named `app`, which the cluster DNS resolves similarly.

---

### 📄 `backend/Dockerfile` — Building the Node.js Container

```dockerfile
FROM node:18-alpine

LABEL maintainer="FA23-BCS-201"
LABEL description="Quick-Task Hub — Backend API"

WORKDIR /app

COPY package*.json ./

RUN npm install --production

COPY . .

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD wget -qO- http://localhost:3000/api/health || exit 1

CMD ["node", "server.js"]
```

**Every instruction explained:**

| Instruction | What it does |
|---|---|
| `FROM node:18-alpine` | Start from the official lightweight Node.js 18 image (~50MB vs ~900MB full) |
| `LABEL` | Metadata labels for the image (who built it, what it is) |
| `WORKDIR /app` | All subsequent commands run inside `/app` directory in the container |
| `COPY package*.json ./` | Copy only dependency manifests FIRST (important for layer caching!) |
| `RUN npm install --production` | Install only production dependencies — skips devDependencies to keep image smaller |
| `COPY . .` | Now copy the full source code (after dependencies, so code changes don't invalidate the npm install cache layer) |
| `EXPOSE 3000` | Documents that this container uses port 3000 (doesn't actually open it — that's done by docker-compose or K8s) |
| `HEALTHCHECK` | Docker will ping `/api/health` every 30s — if it fails 3 times, the container is marked `unhealthy` |
| `CMD ["node", "server.js"]` | The default command that runs when the container starts |

> **Why copy `package*.json` before the full source?**
> Docker builds images in layers. If you copy source code first, every code change triggers `npm install` to re-run, which is slow. By copying `package.json` first and running `npm install`, Docker caches that layer. Subsequent builds only re-run `npm install` if `package.json` actually changed.

---

### 📄 `frontend/Dockerfile` — Building the Nginx Container

```dockerfile
FROM nginx:alpine

LABEL maintainer="FA23-BCS-201"
LABEL description="Quick-Task Hub — Frontend (Nginx)"

RUN rm -rf /usr/share/nginx/html/*

COPY index.html /usr/share/nginx/html/index.html

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

**Every instruction explained:**

| Instruction | What it does |
|---|---|
| `FROM nginx:alpine` | Start from Nginx Alpine (~23MB) — tiny, secure, production-ready |
| `RUN rm -rf /usr/share/nginx/html/*` | Remove the default Nginx welcome page |
| `COPY index.html /usr/share/nginx/html/` | Place our custom single-page app as the website root |
| `COPY nginx.conf /etc/nginx/conf.d/default.conf` | Replace default Nginx config with our custom config (including the /api/ proxy) |
| `EXPOSE 80` | Documents the HTTP port |
| `CMD ["nginx", "-g", "daemon off;"]` | Start Nginx in foreground mode — required for Docker (containers exit when the main process exits) |

---

➡️ **Next:** See [03-docker-and-compose.md](./03-docker-and-compose.md) for Docker Compose and containerization deep-dive.

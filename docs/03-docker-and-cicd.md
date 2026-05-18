# 📘 PART 3 — Docker Compose & CI/CD Pipeline Deep Dive
### Quick-Task Hub | DevOps Final Exam | FA23-BCS-201

---

## 🐳 DOCKER COMPOSE — Local Multi-Container Orchestration

`docker-compose.yml` is the local development equivalent of Kubernetes. It defines all three containers and their relationships in a single file.

---

### 📄 `docker-compose.yml` — Full Annotated Walkthrough

```yaml
# ── Networks ─────────────────────────────────────────────────────
networks:
  app-network:
    driver: bridge
```
> Creates a **private virtual network** named `app-network` using Docker's bridge driver. All three containers are connected to this network. Containers can reach each other using their **service name as the hostname** (e.g., `mongo`, `app`, `frontend`). Traffic on this network never leaves the host machine.

```yaml
# ── Volumes ──────────────────────────────────────────────────────
volumes:
  mongo_data:
    driver: local
```
> Creates a **named Docker volume** called `mongo_data`. This is a persistent storage area managed by Docker on the host machine. Even if you run `docker-compose down`, this volume survives. You'd need `docker-compose down -v` to delete it. Without this, every time MongoDB restarts, all tasks would be wiped.

---

#### Service 1: MongoDB

```yaml
services:
  mongo:
    image: mongo:7
    container_name: task-mongo
    restart: unless-stopped
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 20s
```

| Key | Value | Meaning |
|---|---|---|
| `image: mongo:7` | Official MongoDB 7 image | Pull from Docker Hub — no custom Dockerfile needed |
| `container_name: task-mongo` | Fixed name | Makes it easy to identify in `docker ps` |
| `restart: unless-stopped` | Auto-restart | Restarts automatically on crash unless explicitly stopped |
| `ports: "27017:27017"` | Host:Container | Exposes MongoDB locally so you can connect with MongoDB Compass or `mongosh` |
| `volumes: mongo_data:/data/db` | Named volume | MongoDB stores all data in `/data/db` inside the container — we map it to the persistent named volume |
| `healthcheck` | Health probe | Runs `mongosh --eval "db.adminCommand('ping')"` every 30 seconds — if it fails 5 times, container is `unhealthy` |

---

#### Service 2: Backend (Node.js API)

```yaml
  app:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: quick-task-backend
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - MONGO_URI=mongodb://mongo:27017/taskdb
      - PORT=3000
    depends_on:
      mongo:
        condition: service_healthy
    networks:
      - app-network
```

| Key | Value | Meaning |
|---|---|---|
| `build.context: ./backend` | Build from `./backend` directory | Docker uses the `backend/` folder as the build context |
| `build.dockerfile: Dockerfile` | Use `backend/Dockerfile` | Explicitly names the Dockerfile to use |
| `environment` | Env vars | Injects `MONGO_URI` and `PORT` into the container — `server.js` reads these via `process.env` |
| `MONGO_URI=mongodb://mongo:27017/taskdb` | Uses Docker DNS | `mongo` is the service name → Docker resolves it to the MongoDB container's IP automatically |
| `depends_on.mongo.condition: service_healthy` | Startup ordering | The backend will NOT start until the `mongo` service passes its healthcheck — prevents "could not connect to MongoDB" errors |

---

#### Service 3: Frontend (Nginx)

```yaml
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: quick-task-frontend
    restart: unless-stopped
    ports:
      - "8080:80"
    depends_on:
      - app
    networks:
      - app-network
```

| Key | Value | Meaning |
|---|---|---|
| `ports: "8080:80"` | 8080 on host → 80 in container | Port 80 on Windows is blocked by system services. We map it to 8080 on the host to avoid permission errors. Inside the container it still runs on 80. |
| `depends_on: app` | Startup order | Frontend starts after the backend is up |

---

### 🔧 Common Docker Compose Commands

```powershell
# Start all services in background (detached mode), rebuild images
docker-compose up -d --build

# Check running containers and health status
docker-compose ps

# Follow logs from all containers in real time
docker-compose logs -f

# Follow logs from only the backend
docker-compose logs -f app

# Stop all containers (keep volumes)
docker-compose down

# Stop and DELETE volumes (wipes MongoDB data)
docker-compose down -v

# Rebuild only a specific service
docker-compose build app

# Restart a specific service
docker-compose restart frontend
```

---

## ⚙️ CI/CD PIPELINE — GitHub Actions Deep Dive

The file `.github/workflows/ci-cd.yml` is the heart of the automation. Every time code is pushed to the `main` branch, GitHub automatically runs all 4 stages.

---

### How GitHub Actions Works

GitHub Actions is event-driven automation. The `on:` block defines the **triggers**:

```yaml
on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]
```
- **`push`** — runs the full pipeline (all 4 stages) on every `git push origin main`
- **`pull_request`** — runs only Stages 1 & 2 (Build + Test) on PRs, to validate before merging. Docker Push and AKS Deploy are **skipped** on PRs (see `if: github.event_name == 'push'` conditions below)

---

### Global Environment Variables

```yaml
env:
  DOCKERHUB_USERNAME: itzbaig
  BACKEND_IMAGE: itzbaig/fa23-bcs-201
  FRONTEND_IMAGE: itzbaig/fa23-bcs-201-frontend
```
> These are available in all jobs as `${{ env.BACKEND_IMAGE }}` etc. Defined once here so if you ever change the Docker Hub username, you change it in one place.

---

### Stage 1: 🔨 Build

```yaml
  build:
    name: 🔨 Build
    runs-on: ubuntu-latest
    steps:
      - name: Checkout source code
        uses: actions/checkout@v4

      - name: Set up Node.js 18
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: backend/package-lock.json

      - name: Install backend dependencies
        working-directory: ./backend
        run: npm install

      - name: Verify backend files
        working-directory: ./backend
        run: |
          echo "✅ Backend files:"
          ls -la
          echo "✅ Node version: $(node -v)"
          echo "✅ NPM version: $(npm -v)"
```

**What happens:**
1. GitHub provisions a fresh Ubuntu 22.04 virtual machine (the "runner")
2. `actions/checkout@v4` — clones your repository into the runner
3. `actions/setup-node@v4` — installs Node.js 18 with NPM cache enabled (speeds up repeated runs)
4. `npm install` — downloads all dependencies from `package.json`
5. Verifies that files exist and prints Node/NPM versions for debugging

**Purpose:** Validates that the code structure is valid and dependencies can be installed. Catches missing files, broken `package.json`, or incompatible Node versions early.

---

### Stage 2: 🧪 Test

```yaml
  test:
    name: 🧪 Test
    runs-on: ubuntu-latest
    needs: build
    services:
      mongo:
        image: mongo:7
        ports:
          - 27017:27017
        options: >-
          --health-cmd "mongosh --eval \"db.adminCommand('ping')\""
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
```

> **`needs: build`** — Stage 2 only runs if Stage 1 succeeded. This enforces the pipeline dependency chain.
>
> **`services:`** — GitHub Actions can spin up Docker sidecar containers alongside the test runner. Here, a real MongoDB 7 container is started and health-checked before the tests run. This means the tests connect to a **real database**, not a mock!

```yaml
      - name: Start backend server
        working-directory: ./backend
        env:
          MONGO_URI: mongodb://localhost:27017/taskdb_test
          PORT: 3000
        run: |
          node server.js &
          sleep 5
          echo "✅ Backend started"
```
> The `&` at the end of `node server.js &` runs the server in the background. Then `sleep 5` gives it 5 seconds to fully start before running tests against it.

```yaml
      - name: Run API health check test
        run: |
          STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/api/health)
          if [ "$STATUS" != "200" ]; then
            echo "❌ Health check failed with status $STATUS"
            exit 1
          fi
          echo "✅ Health check passed"
```
> Uses `curl` to hit the health endpoint and capture only the HTTP status code (`%{http_code}`). If it's not `200`, the pipeline fails with `exit 1`.

```yaml
      - name: Run tasks API test (POST + GET)
        run: |
          RESP=$(curl -s -X POST http://localhost:3000/api/tasks \
            -H "Content-Type: application/json" \
            -d '{"title":"CI Test Task","priority":"high","status":"pending"}')
          TITLE=$(echo $RESP | python3 -c "import sys,json; print(json.load(sys.stdin)['title'])")
          if [ "$TITLE" != "CI Test Task" ]; then
            exit 1
          fi
```
> Creates a real task via the API, then parses the JSON response using Python's `json` module (available on Ubuntu runners) to verify the `title` field was saved correctly.

---

### Stage 3: 🐳 Docker Build & Push

```yaml
  docker:
    name: 🐳 Docker Build & Push
    runs-on: ubuntu-latest
    needs: test
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
```
> **`needs: test`** — Only runs if tests passed
> **`if: github.ref == 'refs/heads/main' && github.event_name == 'push'`** — Only runs on direct pushes to main, NOT on pull requests

```yaml
      - name: Log in to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
```
> Uses the GitHub repository **Secrets** (`DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`) to authenticate with Docker Hub. These secrets are encrypted and never visible in logs.

```yaml
      - name: Build and push backend image
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          file: ./backend/Dockerfile
          push: true
          tags: |
            ${{ env.BACKEND_IMAGE }}:latest
            ${{ env.BACKEND_IMAGE }}:${{ github.sha }}
```
> **Two tags are pushed:**
> - `itzbaig/fa23-bcs-201:latest` — Always points to the newest build
> - `itzbaig/fa23-bcs-201:<git-commit-sha>` — Immutable tag tied to the exact commit. Enables rollback to any specific commit!

---

### Stage 4: 🚀 Deploy to AKS

```yaml
  deploy:
    name: 🚀 Deploy to AKS
    runs-on: ubuntu-latest
    needs: docker
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    steps:
      - name: Azure Login
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Set AKS context
        uses: azure/aks-set-context@v3
        with:
          resource-group: devops-midterm-rg
          cluster-name: student-app-aks
```
> `azure/login@v1` authenticates using the `AZURE_CREDENTIALS` secret (the full Service Principal JSON).
> `azure/aks-set-context@v3` runs `az aks get-credentials` internally, configuring `kubectl` to talk to your cluster.

```yaml
      - name: Apply Kubernetes manifests
        run: |
          kubectl apply -f k8s/mongo-pvc.yaml
          kubectl apply -f k8s/deployment.yaml
          kubectl apply -f k8s/service.yaml

      - name: Force rollout with latest images
        run: |
          kubectl rollout restart deployment/quick-task-backend
          kubectl rollout restart deployment/quick-task-frontend

      - name: Wait for rollout to complete
        run: |
          kubectl rollout status deployment/quick-task-backend --timeout=120s
          kubectl rollout status deployment/quick-task-frontend --timeout=120s
```

> **`kubectl apply -f`** — applies manifests in idempotent fashion (creates if not exists, updates if changed, does nothing if identical)
>
> **`kubectl rollout restart`** — forces pods to pull the latest Docker image (since `imagePullPolicy: Always` is set). Without this, Kubernetes would keep running old pods if the `:latest` tag hasn't changed.
>
> **`kubectl rollout status --timeout=120s`** — blocks the pipeline and watches the rollout. If pods fail to become Ready within 120 seconds, the pipeline fails. This ensures we know immediately if a deployment broke production.

---

### 🔐 GitHub Secrets Required

Go to: **GitHub Repo → Settings → Secrets and Variables → Actions**

| Secret Name | Value | How to Get |
|---|---|---|
| `DOCKERHUB_USERNAME` | `itzbaig` | Your Docker Hub username |
| `DOCKERHUB_TOKEN` | `<token>` | Docker Hub → Account Settings → Security → New Access Token |
| `AZURE_CREDENTIALS` | `{...JSON...}` | Run: `az ad sp create-for-rbac --name "github-actions-sp-final" --role contributor --scopes /subscriptions/<SUB_ID>/resourceGroups/devops-midterm-rg --sdk-auth` |

---

### 📊 Pipeline Execution Flow

```
git push origin main
        │
        ▼
┌─────────────────────┐
│  Stage 1: 🔨 BUILD  │  ← Always runs on push/PR
│  npm install        │
│  verify files       │
└──────────┬──────────┘
           │ on success
           ▼
┌─────────────────────┐
│  Stage 2: 🧪 TEST   │  ← Always runs on push/PR
│  start MongoDB      │
│  start backend      │
│  curl /api/health   │
│  POST + GET task    │
└──────────┬──────────┘
           │ on success + push to main only
           ▼
┌─────────────────────────────────┐
│  Stage 3: 🐳 DOCKER BUILD+PUSH  │
│  docker login                   │
│  build backend image            │
│  build frontend image           │
│  push :latest + :<sha> tags     │
└──────────┬──────────────────────┘
           │ on success + push to main only
           ▼
┌─────────────────────────────────┐
│  Stage 4: 🚀 DEPLOY TO AKS      │
│  az login (service principal)   │
│  kubectl apply manifests        │
│  rollout restart                │
│  wait for rollout complete      │
│  kubectl get pods + svc         │
└─────────────────────────────────┘
```

---

➡️ **Next:** See [04-kubernetes-manifests.md](./04-kubernetes-manifests.md) for the full Kubernetes YAML walkthrough.

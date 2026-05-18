# ⚡ Quick-Task Hub

### DevOps Final Exam Project | FA23-BCS-201

A **3-tier cloud-native task management application** built and deployed using modern DevOps practices.

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Browser                             │
└─────────────────────┬───────────────────────────────────────┘
                       │ HTTP :80
┌─────────────────────▼───────────────────────────────────────┐
│              Frontend — Nginx (Static HTML)                  │
│        Serves index.html | Proxies /api/ → Backend           │
└─────────────────────┬───────────────────────────────────────┘
                       │ HTTP :3000
┌─────────────────────▼───────────────────────────────────────┐
│              Backend — Node.js / Express API                 │
│        REST API: /api/tasks  /api/health                     │
└─────────────────────┬───────────────────────────────────────┘
                       │ MongoDB Protocol :27017
┌─────────────────────▼───────────────────────────────────────┐
│              Database — MongoDB 7                            │
│        Persistent volume | Collection: tasks                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
devopsMidTerm/
├── frontend/
│   ├── index.html          # Single-page task management UI
│   ├── Dockerfile          # Nginx container for static frontend
│   └── nginx.conf          # Nginx config with /api/ proxy
├── backend/
│   ├── server.js           # Express app entry point
│   ├── routes/tasks.js     # CRUD API routes for tasks
│   ├── package.json        # Node.js dependencies
│   └── Dockerfile          # Node.js container for backend
├── k8s/
│   ├── mongo-pvc.yaml      # PersistentVolumeClaim for MongoDB
│   ├── deployment.yaml     # K8s Deployments (frontend, backend, mongo)
│   └── service.yaml        # K8s Services (LoadBalancer + ClusterIP)
├── selenium/
│   ├── requirements.txt    # Python Selenium dependencies
│   ├── README.md           # Test run instructions
│   └── tests/
│       └── test_suite.py   # 4 automated Selenium test cases
├── .github/
│   └── workflows/
│       └── ci-cd.yml       # GitHub Actions CI/CD pipeline (4 stages)
├── docker-compose.yml      # 3-service local development stack
└── DEVOPS_EXAM_GUIDE.md    # Deployment guide with screenshots checklist
```

---

## 🐳 Section A: Containerization

### Dockerfiles

| Service  | File                         | Base Image         |
| -------- | ---------------------------- | ------------------ |
| Frontend | `frontend/Dockerfile`      | `nginx:alpine`   |
| Backend  | `backend/Dockerfile`       | `node:18-alpine` |
| Database | `mongo:7` (official image) | —                 |

### Run Locally with Docker Compose

```powershell
# Build and start all 3 services
docker-compose up -d --build

# Verify all containers are running
docker-compose ps

# View logs
docker-compose logs -f
```

**Services:**

| Container               | Port       | Description            |
| ----------------------- | ---------- | ---------------------- |
| `quick-task-frontend` | `:8080`  | Nginx serving frontend |
| `quick-task-backend`  | `:3000`  | Express REST API       |
| `task-mongo`          | `:27017` | MongoDB database       |

Access the app at: **http://localhost:8080**

---

## ⚙️ Section B: CI/CD Pipeline (GitHub Actions)

Pipeline file: `.github/workflows/ci-cd.yml`

**Triggers:** Push to `main` branch or Pull Request.

```
┌──────────┐    ┌──────────┐    ┌────────────────────┐    ┌──────────────┐
│  Build   │───▶│   Test   │───▶│  Docker Build+Push │───▶│  Deploy AKS  │
│ (Node.js)│    │ (API+DB) │    │  (Docker Hub)      │    │  (kubectl)   │
└──────────┘    └──────────┘    └────────────────────┘    └──────────────┘
```

### Required GitHub Secrets

| Secret                 | Description                  |
| ---------------------- | ---------------------------- |
| `DOCKERHUB_USERNAME` | `itzbaig`                  |
| `DOCKERHUB_TOKEN`    | Docker Hub access token      |
| `AZURE_CREDENTIALS`  | Azure service principal JSON |

### Docker Hub Images

- **Backend:** `itzbaig/fa23-bcs-201:latest`
- **Frontend:** `itzbaig/fa23-bcs-201-frontend:latest`

---

## ☁️ Section C: Kubernetes on AKS

### 1. Generate Azure Service Principal (Credentials Secret)
Run the following unique command to output your `AZURE_CREDENTIALS` JSON secret:
```powershell
az login
az ad sp create-for-rbac --name "github-actions-sp-final" --role contributor --scopes /subscriptions/c3673867-9db1-4e60-8f78-6ca0e354bf8c/resourceGroups/devops-midterm-rg --sdk-auth
```

### 2. Connect to your Cluster
Connect to your lightweight AKS cluster running in the policy-approved region:
```powershell
az aks get-credentials --resource-group devops-midterm-rg --name student-app-aks --overwrite-existing
```

### 3. Deploy Manifests
Deploy the database storage volume, server configurations, and ingress LoadBalancer:
```powershell
# Apply resources in order
kubectl apply -f k8s/mongo-pvc.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Restart pods to pull latest images from Docker Hub
kubectl rollout restart deployment/quick-task-backend
kubectl rollout restart deployment/quick-task-frontend

# Monitor deployment progress
kubectl get pods
kubectl get svc
```

Access the live cloud deployment at: **[http://4.224.235.81](http://4.224.235.81)**

### K8s Resources

| Resource                   | Kind                   | Description                    |
| -------------------------- | ---------------------- | ------------------------------ |
| `mongo`                  | Deployment             | MongoDB database pod           |
| `quick-task-backend`     | Deployment             | Node.js API pod                |
| `quick-task-frontend`    | Deployment             | Nginx frontend pod             |
| `mongo-pvc`              | PVC                    | Persistent storage for MongoDB |
| `mongo-service`          | Service (ClusterIP)    | Internal DB access             |
| `app`                    | Service (ClusterIP)    | Internal backend access        |
| `quick-task-hub-service` | Service (LoadBalancer) | **Public Azure IP** (http://4.224.235.81) |

---

## 🧪 Section D: Selenium Automated Testing

The Selenium testing suite is built using `pytest` and runs **100% offline and instantly** using a locally bundled `chromedriver.exe` inside the [selenium/chromedriver.exe](file:///c:/Users/Hassan/DevopsProjects/devopsMidTerm/selenium/chromedriver.exe) folder, perfectly matching Google Chrome version `148`.

### Run the Test Suite
```powershell
# Install offline dependencies
pip install -r selenium/requirements.txt

# Run the 14 test methods inside the 4 core test cases
python -m pytest selenium/tests/test_suite.py -v --html=report.html --self-contained-html
```

| Test            | Description                                                           |
| --------------- | --------------------------------------------------------------------- |
| **TC-01** | Homepage loads: title, header, form, and 4 stats cards present        |
| **TC-02** | Add task via form — task appears in list and stats update            |
| **TC-03** | Filter buttons (High Priority / Pending / All) work correctly         |
| **TC-04** | `/api/health` returns HTTP 200 with `status: ok` and `db` field |

---

## 🔑 API Reference

| Method     | Endpoint           | Description                                                    |
| ---------- | ------------------ | -------------------------------------------------------------- |
| `GET`    | `/api/health`    | Health check — returns DB status                              |
| `GET`    | `/api/tasks`     | Get all tasks (supports `?status=` & `?priority=` filters) |
| `POST`   | `/api/tasks`     | Create a new task                                              |
| `PATCH`  | `/api/tasks/:id` | Update a task                                                  |
| `DELETE` | `/api/tasks/:id` | Delete a task                                                  |

---

## 👨‍💻 Student Details

- **Registration No:** FA23-BCS-201
- **Name:** Ali Baig
- **Project:** Quick-Task Hub

---

## ⚠️ Cleanup (Run after Viva)

```powershell
az group delete --name devops-midterm-rg --yes --no-wait
```

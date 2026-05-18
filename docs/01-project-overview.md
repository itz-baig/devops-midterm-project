# 📘 PART 1 — Project Overview & Architecture
### Quick-Task Hub | DevOps Final Exam | FA23-BCS-201

---

## 🧠 What Is This Project?

**Quick-Task Hub** is a full-stack, cloud-native **Task Management Web Application** built using a classic **3-tier architecture**:

| Tier | Technology | Role |
|---|---|---|
| **Frontend** | HTML/CSS/JS served by **Nginx** | User interface running in a browser |
| **Backend** | **Node.js + Express** REST API | Business logic, data processing |
| **Database** | **MongoDB 7** | Persistent task storage (NoSQL) |

Everything is containerized with **Docker**, automated through **GitHub Actions CI/CD**, deployed to the cloud on **Azure Kubernetes Service (AKS)**, and tested automatically with **Python Selenium**.

---

## 🗺️ System Architecture Diagram

```
   ┌─────────────────────────────────────────────────────────────────┐
   │                    👤 END USER (Browser)                         │
   └──────────────────────────┬──────────────────────────────────────┘
                               │  HTTP Port 80 (Azure) / 8080 (Local)
   ┌──────────────────────────▼──────────────────────────────────────┐
   │         🌐 FRONTEND — Nginx Container (Port 80)                  │
   │   • Serves static index.html to browser                          │
   │   • Proxies all /api/* requests → Backend on port 3000           │
   │   • Handles gzip compression for performance                     │
   └────────────┬──────────────────────────────────────────────────── ┘
                │  Internal Docker/K8s Network — Port 3000
   ┌────────────▼────────────────────────────────────────────────────┐
   │         ⚙️ BACKEND — Node.js/Express Container (Port 3000)       │
   │   • REST API endpoints: /api/tasks, /api/health                  │
   │   • CRUD operations: GET, POST, PATCH, DELETE                    │
   │   • Mongoose ORM: connects to MongoDB, manages Task schema       │
   └────────────┬────────────────────────────────────────────────────┘
                │  MongoDB Protocol — Port 27017
   ┌────────────▼────────────────────────────────────────────────────┐
   │         🗄️ DATABASE — MongoDB 7 Container (Port 27017)           │
   │   • Stores all tasks in `taskdb` collection                      │
   │   • Data persisted via Docker Volume / Azure PVC                 │
   └─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Full Project Structure Explained

```
devopsMidTerm/
│
├── 📂 frontend/                   ← TIER 1: What users see
│   ├── index.html                 ← Single-page app (UI, CSS, JavaScript)
│   ├── Dockerfile                 ← Builds the Nginx container
│   └── nginx.conf                 ← Web server + API proxy configuration
│
├── 📂 backend/                    ← TIER 2: The brain of the app
│   ├── server.js                  ← Express app entry point
│   ├── routes/
│   │   └── tasks.js               ← All API route handlers + Mongoose schema
│   ├── package.json               ← Node.js dependencies manifest
│   └── Dockerfile                 ← Builds the Node.js container
│
├── 📂 k8s/                        ← CLOUD: Kubernetes deployment manifests
│   ├── mongo-pvc.yaml             ← Persistent disk for MongoDB (Azure CSI)
│   ├── deployment.yaml            ← 3 Pod deployments (mongo, backend, frontend)
│   └── service.yaml               ← 3 K8s Services (2x ClusterIP, 1x LoadBalancer)
│
├── 📂 selenium/                   ← TESTING: Automated UI test suite
│   ├── requirements.txt           ← Python testing dependencies
│   ├── chromedriver.exe           ← Offline bundled Chrome WebDriver v148
│   └── tests/
│       └── test_suite.py          ← 4 Test Classes, 14 Test Methods (pytest)
│
├── 📂 .github/
│   └── workflows/
│       └── ci-cd.yml              ← 4-stage GitHub Actions CI/CD pipeline
│
├── docker-compose.yml             ← Local dev: runs all 3 services together
├── README.md                      ← Quick-start guide
├── FA23-BCS-201.md                ← Formal exam project report
└── docs/                          ← (This deep-dive documentation folder)
```

---

## 🔄 How the Application Works — End-to-End Flow

### Step 1: User Opens the App
The user navigates to either:
- **Local:** `http://localhost:8080`
- **Azure Cloud:** `http://4.224.235.81`

The **Nginx frontend container** serves the `index.html` page to the user's browser. This is a single-page app — all the task UI, forms, and JavaScript are embedded in this one file.

### Step 2: Browser Fetches Tasks
When `index.html` loads, its embedded JavaScript immediately fires a `fetch('/api/tasks')` request.

Nginx sees this request starts with `/api/` and **proxies it** (forwards it) to the backend container (`app:3000`). This is transparent to the user — they never directly connect to the backend.

### Step 3: Backend Queries MongoDB
The Node.js/Express backend receives the GET request at `/api/tasks`, uses Mongoose to query the MongoDB container, and returns a JSON array of all tasks.

### Step 4: UI Renders the Task List
The browser receives the JSON, and the JavaScript in `index.html` dynamically renders each task as a styled card in the task list.

### Step 5: User Adds a Task
User fills the form and clicks "Add Task". The browser sends a `POST /api/tasks` request with JSON data. The backend validates it, saves it to MongoDB via Mongoose, and returns the saved task. The UI refreshes the list automatically.

---

## 🛠️ Technology Stack Summary

| Technology | Version | Purpose |
|---|---|---|
| **Node.js** | 18 LTS | Backend JavaScript runtime |
| **Express.js** | 4.18 | HTTP server & routing framework |
| **Mongoose** | 8.0 | MongoDB ODM (Object Document Mapper) |
| **MongoDB** | 7 | NoSQL database for task persistence |
| **Nginx** | Alpine | Static file server + reverse proxy |
| **Docker** | Latest | Container build and packaging |
| **Docker Compose** | v2 | Multi-container local orchestration |
| **GitHub Actions** | — | CI/CD pipeline automation |
| **Azure AKS** | 1.34.7 | Managed Kubernetes cloud service |
| **kubectl** | — | Kubernetes cluster CLI management |
| **Python** | 3.14 | Selenium test runner language |
| **pytest** | 9.0.3 | Python test framework |
| **Selenium** | Latest | Browser automation for UI testing |
| **ChromeDriver** | 148 | Chrome WebDriver (offline-bundled) |

---

## 🌐 Live URLs

| Environment | URL |
|---|---|
| **Local Development** | http://localhost:8080 |
| **Azure AKS (Cloud)** | http://4.224.235.81 |
| **Backend API Direct** | http://localhost:3000/api/health |
| **GitHub Repository** | https://github.com/itz-baig/devops-midterm-project |
| **Docker Hub (Backend)** | https://hub.docker.com/r/itzbaig/fa23-bcs-201 |
| **Docker Hub (Frontend)** | https://hub.docker.com/r/itzbaig/fa23-bcs-201-frontend |

---

➡️ **Next:** See [02-backend-and-frontend.md](./02-backend-and-frontend.md) for a line-by-line code walkthrough.

# Quick-Task Hub — DevOps Mid-Term Project

A full-stack **Task Management** application built to demonstrate a complete DevOps deployment pipeline.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3, JavaScript (Vanilla) |
| Backend | Node.js v18, Express.js |
| Database | MongoDB 7 |
| Containerization | Docker, Docker Compose |
| Cloud Deployment | Azure Kubernetes Service (AKS) |
| Version Control | Git, GitHub |

## Features

- ➕ Create tasks with title, description, priority, status, and due date
- 🔄 Toggle task status (Pending → In Progress → Completed)
- 🔍 Filter tasks by status or priority
- 🗑️ Delete tasks
- 📊 Live stats dashboard (total, in-progress, completed, high-priority)
- 🟢 Real-time MongoDB connection indicator

## REST API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks` | Get all tasks (supports `?status=` and `?priority=` filters) |
| GET | `/api/tasks/:id` | Get single task |
| POST | `/api/tasks` | Create new task |
| PATCH | `/api/tasks/:id` | Update task |
| DELETE | `/api/tasks/:id` | Delete task |
| GET | `/api/health` | Health check |

## Quick Start

```bash
# Install dependencies
cd backend && npm install

# Run locally (requires MongoDB running on localhost:27017)
node server.js
```

## Docker

```bash
# Build image
docker build -t quick-task-hub:v1 .

# Run with Compose (app + MongoDB)
docker-compose up -d
```

## Deployment Links

- **GitHub:** https://github.com/YOUR_USERNAME/quick-task-hub
- **Docker Hub:** https://hub.docker.com/r/YOUR_USERNAME/quick-task-hub
- **Live App (AKS):** http://YOUR_EXTERNAL_IP/

## Student Info

- **Name:** Hassan
- **Subject:** Cloud Computing / DevOps
- **Project:** Mid-Term Semester Project

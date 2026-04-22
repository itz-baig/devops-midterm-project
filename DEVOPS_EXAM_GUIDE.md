# 🎓 DevOps Mid-Term Exam — Deployment Guide
## Student: FA23-BCS-201 | Project: Quick-Task Hub

This document tracks every stage of your mid-term project. Each part below corresponds to the marking criteria in your `project_requirements.md`.

---

## 🛠 Part 1: Docker & Image Engineering `[8 Marks]`

### 1.1 Verify Docker Installation
Show proof that Docker is ready on your system.
```powershell
docker -v
docker info
```
📸 **SCREENSHOT #1:** Output of these commands.

### 1.2 Build Image with REG NO Tag
The exam requires tagging the image with your Registration Number.
```powershell
cd C:\Users\Hassan\DevopsProjects\devopsMidTerm

# Build the image specifically with your tag
docker build -t fa23-bcs-201:latest .
```
📸 **SCREENSHOT #2:** The build output showing "Successfully tagged fa23-bcs-201:latest".

### 1.3 Local Verification
Run the app and verify it works on your browser.
```powershell
# Run with docker-compose
docker-compose up -d --build

# List images to show your tagged image
docker images
```
📸 **SCREENSHOT #3:** `docker images` showing `fa23-bcs-201`.
📸 **SCREENSHOT #4:** Browser at `http://localhost:3000` showing the "Quick-Task Hub" dashboard.

---

## 📂 Part 2: Git & GitHub Workflow `[5 Marks]`

### 2.1 First Commit (Initial Project)
```powershell
# 1. Initialize
git init

# 2. Add remote (Replace YOUR_USER with your GitHub username)
git remote add origin https://github.com/YOUR_USER/devops-midterm-project.git

# 3. First Commit
git add .
git commit -m "Initial commit: Quick-Task Hub Base Application"
git branch -M main
git push -u origin main
```

### 2.2 Second Commit (Improvement/Fix)
The exam requires a second commit to show history. We added a **Footer** as the improvement.
```powershell
# 1. Check status (you'll see index.html modified)
git status

# 2. Commit the improvement
git add .
git commit -m "Fix: Added academic footer with student details for exam compliance"
git push origin main

# 3. View History
git log --oneline
```
📸 **SCREENSHOT #5:** `git log --oneline` showing at least two commits.

---

## ☁️ Part 3: Cloud Deployment (AKS) `[8 Marks]`

### 3.1 Push to Docker Hub
```powershell
docker login

# Tag for your Docker Hub account
docker tag fa23-bcs-201:latest YOUR_HUB_USER/quick-task-hub:latest

# Push
docker push YOUR_HUB_USER/quick-task-hub:latest
```
📸 **SCREENSHOT #6:** Docker Hub dashboard showing your pushed image.

### 3.2 Kubernetes Deployment
Apply your YAML manifests to the AKS cluster.
```powershell
az login
az aks get-credentials --resource-group devops-midterm-rg --name student-app-aks

# Apply K8s files
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Check pods (Must show Running)
kubectl get pods
```
📸 **SCREENSHOT #7:** `kubectl get pods` showing all pods are "Running".

### 3.3 Public Access & Scaling
```powershell
# Get the External IP
kubectl get svc quick-task-hub-service

# SCALING DEMO (Required for Part 3, Task 6)
kubectl scale deployment quick-task-hub --replicas=3
kubectl get pods
```
📸 **SCREENSHOT #8:** `kubectl get pods` showing 3 replicas running.
📸 **SCREENSHOT #9:** App live at the Azure External IP in your browser.

---

## 🔍 Part 4: Troubleshooting Case `[4 Marks]`

### Scenario: "Failed pod startup due to missing Mongo Service"
If you deploy `quick-task-hub` before `mongo-service` is ready, the app will crash and show **CrashLoopBackOff**.

1.  **Identify:** Pod status is `Error` or `CrashLoopBackOff`.
2.  **Diagnose:** `kubectl logs [pod-name]` shows "Could not connect to MongoDB".
3.  **Fix:** Applied `service.yaml` to ensure the internal `mongo-service` is discoverable by the app.
4.  **Result:** Pods transitioned to `Running`.

📸 **SCREENSHOT #10:** Log output showing a connection error + pods subsequently showing Running.

---

## 📝 Submission Checklist
1. **Filename:** `FA23-BCS-201.pdf` (Print this guide and add screenshots).
2. **GitHub Link:** `https://github.com/Hassan/devops-midterm-project`
3. **Docker Hub Link:** `https://hub.docker.com/r/YOUR_USER/quick-task-hub`
4. **Cloud URL:** `http://[YOUR_AZURE_IP]/`
5. **Azure Architecture:** Justify using **AKS (Kubernetes Service)** + **Azure Load Balancer** for public traffic.

---

### ⚠️ Cleanup (Run after Viva)
To stop Azure from charging your account:
```powershell
az group delete --name devops-midterm-rg --yes --no-wait
```

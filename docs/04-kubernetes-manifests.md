# 📘 PART 4 — Kubernetes Manifests & AKS Cloud Deployment
### Quick-Task Hub | DevOps Final Exam | FA23-BCS-201

---

## ☸️ KUBERNETES — What It Is and Why We Use It

**Docker** lets you run a single container. **Docker Compose** runs multiple containers on one machine. **Kubernetes (K8s)** runs multiple containers across a **cluster of machines** in the cloud with:

- **Self-healing:** Automatically restarts crashed pods
- **Rolling updates:** Deploy new code with zero downtime
- **Scaling:** Add more pods under load with one command
- **Service discovery:** Containers find each other by name, not IP

**Azure Kubernetes Service (AKS)** is Microsoft's managed Kubernetes — Azure handles the Kubernetes control plane (master nodes), we only manage the worker nodes and our deployments.

---

## 🗂️ Our Kubernetes Files

```
k8s/
├── mongo-pvc.yaml      ← Step 1: Create persistent storage for MongoDB
├── deployment.yaml     ← Step 2: Deploy all 3 application pods
└── service.yaml        ← Step 3: Create network access to pods
```

Always apply in this order: **PVC → Deployments → Services**

---

## 📄 `k8s/mongo-pvc.yaml` — Persistent Volume Claim

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mongo-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
  storageClassName: managed-csi
```

### What is a PVC?

A **PersistentVolumeClaim** is a request for storage from the cluster. Think of it as saying:
> "Give me a 1GB disk that only one pod can write to at a time."

Kubernetes fulfills this request by provisioning an **Azure Managed Disk** automatically (because `storageClassName: managed-csi` tells it to use Azure's CSI driver).

### Why is this needed?

MongoDB stores all data in `/data/db` inside its container. Containers are **ephemeral** — when a pod is deleted, restarted, or updated, its filesystem is wiped. Without a PVC, every MongoDB restart would delete all tasks.

With the PVC:
1. Azure creates a persistent disk
2. MongoDB's `/data/db` is mounted to that disk
3. Even if the MongoDB pod is deleted and recreated, the same disk re-attaches with all data intact

### Field-by-field breakdown:

| Field | Value | Meaning |
|---|---|---|
| `kind: PersistentVolumeClaim` | — | This is a storage request resource |
| `name: mongo-pvc` | — | This name is referenced in `deployment.yaml` to mount the volume |
| `accessModes: ReadWriteOnce` | RWO | Only one node can mount this disk for writing at a time (fine for single MongoDB pod) |
| `storage: 1Gi` | 1 Gigabyte | Request 1GB of disk space |
| `storageClassName: managed-csi` | Azure CSI | Use Azure's default storage driver to provision a Managed Disk automatically |

---

## 📄 `k8s/deployment.yaml` — Three Pod Deployments

This file contains **3 separate Kubernetes Deployment resources** separated by `---`.

---

### Deployment 1: MongoDB

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mongo
  labels:
    app: mongo
    tier: database
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mongo
  template:
    metadata:
      labels:
        app: mongo
        tier: database
    spec:
      containers:
      - name: mongo
        image: mongo:7
        ports:
        - containerPort: 27017
        volumeMounts:
        - name: mongo-storage
          mountPath: /data/db
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
      volumes:
      - name: mongo-storage
        persistentVolumeClaim:
          claimName: mongo-pvc
```

**Key concepts explained:**

| Field | Value | Meaning |
|---|---|---|
| `replicas: 1` | 1 | Run exactly 1 MongoDB pod — only 1 because our PVC is `ReadWriteOnce` |
| `selector.matchLabels` | `app: mongo` | The Deployment manages pods that have the label `app: mongo` |
| `template.metadata.labels` | `app: mongo` | Pods created from this template will have these labels — must match `selector.matchLabels` |
| `image: mongo:7` | — | Pull the official MongoDB 7 image from Docker Hub |
| `containerPort: 27017` | — | Documents the port MongoDB listens on (informational, doesn't expose it externally) |
| `volumeMounts.mountPath: /data/db` | — | Mount the PVC at `/data/db` inside the container — MongoDB's default data directory |
| `volumes.persistentVolumeClaim.claimName: mongo-pvc` | — | Reference the PVC we created in `mongo-pvc.yaml` |
| `resources.requests` | 256Mi / 250m | Kubernetes scheduler uses these to find a node with enough capacity |
| `resources.limits` | 512Mi / 500m | Hard caps — if MongoDB exceeds 512Mi RAM, the pod is OOMKilled and restarted |

> **CPU units:** `250m` = 250 millicores = 0.25 CPU cores. `1000m` = 1 full core.

---

### Deployment 2: Backend (Node.js API)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: quick-task-backend
  labels:
    app: quick-task-backend
    tier: backend
spec:
  replicas: 1
  selector:
    matchLabels:
      app: quick-task-backend
  template:
    spec:
      containers:
      - name: quick-task-backend
        image: itzbaig/fa23-bcs-201:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 3000
        env:
        - name: MONGO_URI
          value: "mongodb://mongo-service:27017/taskdb"
        - name: PORT
          value: "3000"
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "300m"
        readinessProbe:
          httpGet:
            path: /api/health
            port: 3000
          initialDelaySeconds: 15
          periodSeconds: 10
```

**Critical fields:**

| Field | Value | Why it matters |
|---|---|---|
| `image: itzbaig/fa23-bcs-201:latest` | Docker Hub image | Kubernetes pulls this from Docker Hub — this is the image pushed by the CI/CD pipeline |
| `imagePullPolicy: Always` | Always pull | Forces Kubernetes to check Docker Hub for a newer image on every pod creation. Without this, K8s might use a cached old image even when `:latest` was updated |
| `MONGO_URI: mongodb://mongo-service:27017/taskdb` | K8s DNS name | In Kubernetes, containers reach each other via **Service names**, not container names. `mongo-service` is the name of the ClusterIP Service defined in `service.yaml` |
| `readinessProbe.httpGet.path: /api/health` | Health endpoint | Kubernetes probes this endpoint every 10 seconds after a 15-second initial wait. The pod only receives traffic when this returns HTTP 200. Prevents sending traffic to pods that are still starting |
| `readinessProbe.initialDelaySeconds: 15` | 15 second wait | Gives Node.js time to start and connect to MongoDB before probes begin |

---

### Deployment 3: Frontend (Nginx)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: quick-task-frontend
  labels:
    app: quick-task-frontend
    tier: frontend
spec:
  replicas: 1
  selector:
    matchLabels:
      app: quick-task-frontend
  template:
    spec:
      containers:
      - name: quick-task-frontend
        image: itzbaig/fa23-bcs-201-frontend:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "64Mi"
            cpu: "50m"
          limits:
            memory: "128Mi"
            cpu: "100m"
```

> No `readinessProbe` here — Nginx starts almost instantly. Very lightweight: only 64Mi RAM, 50m CPU requested. This is appropriate for a static file server.

---

## 📄 `k8s/service.yaml` — Three Kubernetes Services

A **Service** is a stable network endpoint for a set of pods. Pods get random IPs that change on every restart — Services provide a fixed name and IP that never changes.

---

### Service 1: MongoDB (ClusterIP — Internal Only)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: mongo-service
  labels:
    app: mongo
spec:
  selector:
    app: mongo
  ports:
  - protocol: TCP
    port: 27017
    targetPort: 27017
  type: ClusterIP
```

| Field | Meaning |
|---|---|
| `name: mongo-service` | DNS name inside the cluster. Backend uses `mongodb://mongo-service:27017` |
| `selector: app: mongo` | Routes traffic to pods with the label `app: mongo` (our MongoDB pods) |
| `type: ClusterIP` | Only accessible from within the cluster — MongoDB is never exposed to the internet! |
| `port: 27017` | The port this Service listens on |
| `targetPort: 27017` | The port on the pod that traffic is forwarded to |

---

### Service 2: Backend (ClusterIP — Internal Only)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: app
  labels:
    app: quick-task-backend
spec:
  selector:
    app: quick-task-backend
  ports:
  - protocol: TCP
    port: 3000
    targetPort: 3000
  type: ClusterIP
```

> **Why is this named `app`?** Because `nginx.conf` proxies to `http://app:3000/api/`. The Service name **must match** what Nginx uses as the upstream hostname. The cluster's DNS resolves `app` → the ClusterIP → the backend pods.

---

### Service 3: Frontend (LoadBalancer — Public Internet Access!)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: quick-task-hub-service
  labels:
    app: quick-task-frontend
spec:
  selector:
    app: quick-task-frontend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
  type: LoadBalancer
```

| Field | Meaning |
|---|---|
| `type: LoadBalancer` | Azure automatically provisions an Azure Load Balancer with a **public IP** |
| `port: 80` | The public internet port — users visit `http://<EXTERNAL-IP>` |
| `targetPort: 80` | Forwards to port 80 on the Nginx pods |
| `selector: app: quick-task-frontend` | Routes traffic to frontend pods only |

> Once applied, run `kubectl get svc` and wait for `EXTERNAL-IP` to change from `<pending>` to a real IP (takes ~60 seconds for Azure to provision). Our live IP: **`4.224.235.81`**

---

## 🖥️ Complete AKS Setup Commands

### 1. Create the AKS Cluster (first time only)
```powershell
az login
az aks create `
  --resource-group devops-midterm-rg `
  --name student-app-aks `
  --location centralindia `
  --node-count 1 `
  --node-vm-size standard_b2s_v2 `
  --generate-ssh-keys
```

### 2. Connect Local kubectl to AKS
```powershell
az aks get-credentials --resource-group devops-midterm-rg --name student-app-aks --overwrite-existing
kubectl get nodes    # Should show 1 node in Ready state
```

### 3. Deploy the Application
```powershell
# Apply in order
kubectl apply -f k8s/mongo-pvc.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

### 4. Monitor and Verify
```powershell
# Watch pods come up in real time
kubectl get pods -w

# Check services and get public IP
kubectl get svc

# View logs from a specific pod
kubectl logs <pod-name>

# Get detailed info about a pod (useful for debugging)
kubectl describe pod <pod-name>
```

### 5. Update to Latest Docker Images
```powershell
kubectl rollout restart deployment/quick-task-backend
kubectl rollout restart deployment/quick-task-frontend
kubectl rollout status deployment/quick-task-backend --timeout=120s
```

### 6. Scale a Deployment
```powershell
# Scale backend to 3 replicas
kubectl scale deployment quick-task-backend --replicas=3
kubectl get pods    # Now shows 3 backend pods
```

---

## 🔍 How Kubernetes Routes Traffic (End-to-End)

```
Internet User
     │
     ▼
Azure Load Balancer (public IP: 4.224.235.81:80)
     │
     ▼  [quick-task-hub-service LoadBalancer]
Nginx Pod (port 80)
     │
     │  Request: GET /api/tasks
     ▼  [nginx.conf proxies /api/ to http://app:3000]
Kubernetes DNS resolves "app" → ClusterIP Service
     │
     ▼  [app ClusterIP Service on port 3000]
Node.js/Express Pod (port 3000)
     │
     │  mongoose.find({}) query
     ▼  [mongo-service ClusterIP on port 27017]
MongoDB Pod (port 27017)
     │
     ▼
Azure Managed Disk (PVC: mongo-pvc, /data/db)
```

---

➡️ **Next:** See [05-selenium-testing.md](./05-selenium-testing.md) for the complete Selenium test suite breakdown.

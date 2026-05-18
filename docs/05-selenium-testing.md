# 📘 PART 5 — Selenium Testing, Viva Q&A & Quick Reference
### Quick-Task Hub | DevOps Final Exam | FA23-BCS-201

---

## 🧪 SELENIUM TESTING — Complete Breakdown

Selenium is a browser automation tool. It opens a real Chrome browser (headlessly — no visible window), clicks buttons, fills forms, reads text, and asserts expected results — just like a human tester would, but automated.

---

### 🔧 Setup & Dependencies

#### `selenium/requirements.txt`

```
selenium          ← Core browser automation library
pytest            ← Test runner framework (collects and runs test classes/methods)
pytest-html       ← Generates a beautiful HTML test report
webdriver-manager ← (installed but overridden by local driver)
requests          ← HTTP client for direct API tests (TC-04)
```

#### Install:
```powershell
pip install -r selenium/requirements.txt
```

#### Run:
```powershell
# Basic run
python -m pytest selenium/tests/test_suite.py -v

# With HTML report
python -m pytest selenium/tests/test_suite.py -v --html=report.html --self-contained-html
```

---

### 🚗 The ChromeDriver — Why It's Bundled Locally

Selenium needs a **WebDriver executable** to control Chrome. Normally, tools like `webdriver-manager` download this automatically from Google's servers — but this can be **extremely slow or time out** on some networks.

**Our Solution:** The `chromedriver.exe` (version 148, matching Chrome 148 installed on the host) is bundled directly in `selenium/chromedriver.exe`.

The test suite locates it using a relative path:
```python
local_driver = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "chromedriver.exe")
)
service = Service(executable_path=local_driver)
```

This means:
- ✅ No network required
- ✅ Works instantly every time
- ✅ Portable — anyone who clones the repo can run tests immediately

---

### 🔧 The Pytest Fixture — `driver`

```python
@pytest.fixture(scope="module")
def driver():
    """Set up headless Chrome WebDriver using locally bundled chromedriver.exe."""
    options = Options()
    options.add_argument("--headless")           # No GUI window
    options.add_argument("--no-sandbox")         # Required in containerized environments
    options.add_argument("--disable-dev-shm-usage")  # Prevent /dev/shm memory issues
    options.add_argument("--window-size=1280,800")   # Fixed viewport size

    local_driver = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "chromedriver.exe"))
    service = Service(executable_path=local_driver)

    drv = webdriver.Chrome(service=service, options=options)
    drv.implicitly_wait(10)  # Wait up to 10 seconds for elements before throwing errors

    yield drv   # Provide the driver to all tests

    drv.quit()  # Cleanup: close browser after all tests complete
```

**`scope="module"`** means this fixture runs **once** for the entire test file — the same browser instance is reused across all test classes (much faster than opening/closing Chrome for each test).

**`yield drv`** is the pytest pattern for fixtures with cleanup — everything before `yield` is setup, everything after is teardown.

---

## 📋 TC-01: Homepage Loads (4 Methods)

```python
class TestHomepageLoads:
    """TC-01 — Verify the homepage loads with the correct title and key elements."""
```

### Method 1: `test_page_title`
```python
def test_page_title(self, driver):
    driver.get(BASE_URL)
    time.sleep(2)
    assert "Quick-Task" in driver.title
```
- Opens `http://localhost:8080` in headless Chrome
- Waits 2 seconds for full page load
- Asserts that the browser tab title contains `"Quick-Task"`

### Method 2: `test_header_visible`
```python
def test_header_visible(self, driver):
    driver.get(BASE_URL)
    header = driver.find_element(By.TAG_NAME, "header")
    assert header.is_displayed()
    assert "Quick-Task Hub" in header.text
```
- Finds the `<header>` HTML element
- Checks it is visible on screen
- Checks it contains the text `"Quick-Task Hub"`

### Method 3: `test_add_task_form_present`
```python
def test_add_task_form_present(self, driver):
    form = driver.find_element(By.ID, "taskForm")
    assert form.is_displayed()
```
- Finds the element with `id="taskForm"`
- Verifies the form is displayed

### Method 4: `test_stats_section_present`
```python
def test_stats_section_present(self, driver):
    stats = driver.find_elements(By.CLASS_NAME, "stat")
    assert len(stats) == 4
```
- Finds all elements with CSS class `"stat"`
- Asserts exactly **4** stat cards are present (Total, In Progress, Completed, High Priority)

---

## 📋 TC-02: Add a New Task (2 Methods)

```python
class TestAddTask:
    TASK_TITLE = "Selenium Automated Test Task"
```

### Method 1: `test_add_task_via_form`
```python
def test_add_task_via_form(self, driver):
    driver.get(BASE_URL)
    wait = WebDriverWait(driver, 15)

    title_input = wait.until(EC.presence_of_element_located((By.ID, "title")))
    title_input.clear()
    title_input.send_keys(self.TASK_TITLE)

    desc_input = driver.find_element(By.ID, "description")
    desc_input.send_keys("Created by Selenium TC-02 automated test")

    priority_select = Select(driver.find_element(By.ID, "priority"))
    priority_select.select_by_value("high")

    status_select = Select(driver.find_element(By.ID, "status"))
    status_select.select_by_value("in-progress")

    add_btn = driver.find_element(By.ID, "addBtn")
    add_btn.click()

    time.sleep(2)
    task_list = driver.find_element(By.ID, "taskList")
    assert self.TASK_TITLE in task_list.text
```

**Step by step:**
1. `WebDriverWait(driver, 15)` — explicit wait up to 15 seconds (smarter than `time.sleep`)
2. `EC.presence_of_element_located` — waits until the `#title` input exists in DOM
3. `title_input.send_keys()` — types text into the input field
4. `Select(element).select_by_value()` — changes a `<select>` dropdown to the specified `<option value="">`
5. `add_btn.click()` — clicks the submit button
6. After 2 seconds, checks the task list contains the task title

### Method 2: `test_stats_update_after_add`
```python
def test_stats_update_after_add(self, driver):
    total_stat = driver.find_element(By.ID, "statTotal")
    count = int(total_stat.text)
    assert count >= 1
```
- Reads the `#statTotal` element (the "Total Tasks" counter)
- Converts the displayed number to `int`
- Asserts it's at least 1 (since TC-02 just added a task)

---

## 📋 TC-03: Filter Tasks (3 Methods)

```python
class TestFilterTasks:
    """TC-03 — Click filter buttons and verify they become active."""
```

### Method 1: `test_high_priority_filter`
```python
filter_btn = wait.until(
    EC.element_to_be_clickable((By.XPATH, "//button[@data-filter='high']"))
)
filter_btn.click()
btn_classes = filter_btn.get_attribute("class")
assert "active" in btn_classes
```
- **XPath selector:** `//button[@data-filter='high']` — finds a `<button>` element where the `data-filter` attribute equals `'high'`
- `EC.element_to_be_clickable` — waits until the button is both visible and interactable
- After clicking, checks that CSS class `"active"` was added (meaning the filter is now selected)

### Method 2: `test_all_filter_resets`
- Clicks High Priority filter first, then clicks "All" filter
- Verifies "All" button has `active` class after reset

### Method 3: `test_pending_filter`
- Clicks the `data-filter='pending'` button
- Verifies it gets `active` class

---

## 📋 TC-04: API Health Check (5 Methods)

These tests use the `requests` library to call the backend API **directly** (bypassing the browser and Nginx).

### Method 1: `test_health_endpoint_status_code`
```python
response = requests.get(f"{API_URL}/api/health", timeout=10)
assert response.status_code == 200
```
- `API_URL = "http://localhost:3000"` — direct to backend port
- Asserts HTTP 200 OK

### Method 2: `test_health_endpoint_json_structure`
```python
data = response.json()
assert "status" in data
assert data["status"] == "ok"
```
- Parses the JSON response
- Checks for `"status": "ok"`

### Method 3: `test_health_endpoint_db_status`
```python
assert "db" in data
assert data["db"] in ("connected", "disconnected")
```
- Checks the `"db"` field exists
- Accepts either value (doesn't fail if DB is temporarily disconnected)

### Method 4: `test_tasks_api_endpoint`
```python
response = requests.get(f"{API_URL}/api/tasks", timeout=10)
assert response.status_code == 200
assert isinstance(response.json(), list)
```
- Hits `GET /api/tasks`
- Asserts the response is a JSON **array** (not an object or string)

### Method 5: `test_db_indicator_on_page`
```python
def test_db_indicator_on_page(self, driver):
    driver.get(BASE_URL)
    time.sleep(3)
    db_label = driver.find_element(By.ID, "dbLabel")
    label_text = db_label.text
    assert "Connected" in label_text or "Disconnected" in label_text
```
- Uses the browser driver (not requests)
- Finds the `#dbLabel` element (the green/red DB status pill in the UI)
- Verifies it shows either "Connected" or "Disconnected"

---

## ❓ Viva Question & Answer Preparation

### Q: What is Docker and why use it?
> Docker packages an application and all its dependencies into a **container** — a lightweight, isolated runtime environment. Without Docker, "it works on my machine" is a constant problem. With Docker, the container runs identically on your laptop, your teammate's machine, GitHub's CI runner, and Azure's Kubernetes cluster.

### Q: What is the difference between an image and a container?
> A **Docker image** is a blueprint (like a class in OOP). A **container** is a running instance of that image (like an object). You can run multiple containers from the same image simultaneously.

### Q: What does `docker-compose up --build` do?
> It reads `docker-compose.yml`, builds fresh Docker images from the Dockerfiles (because of `--build`), creates the network and volumes if they don't exist, and starts all 3 services in the correct dependency order.

### Q: Why does the frontend port use 8080 locally but 80 in Kubernetes?
> On Windows, port 80 is reserved by system services (HTTP.sys). We map host port 8080 → container port 80 locally to avoid permission errors. In Kubernetes on Azure, there are no such restrictions, so the LoadBalancer Service exposes port 80 directly to the internet.

### Q: What is the purpose of `depends_on` in Docker Compose?
> `depends_on: mongo: condition: service_healthy` makes the backend wait until MongoDB passes its healthcheck before starting. Without this, the backend might start while MongoDB is still initializing, fail to connect, and crash.

### Q: What is a readinessProbe in Kubernetes?
> A readiness probe tells Kubernetes whether a pod is ready to receive traffic. Our backend probe calls `GET /api/health` every 10 seconds (after a 15-second initial delay). If the response isn't HTTP 200, Kubernetes removes the pod from the Service's load balancer endpoints — users won't hit a pod that isn't ready.

### Q: What is a PersistentVolumeClaim?
> A PVC is a request for storage from the cluster. We request 1Gi of disk space using Azure's `managed-csi` storage class. Azure automatically provisions an Azure Managed Disk and mounts it to our MongoDB pod at `/data/db`. If the pod restarts, the same disk reattaches with all data intact.

### Q: What is the difference between ClusterIP and LoadBalancer service types?
> - **ClusterIP**: Only accessible within the cluster (internal). Used for MongoDB and Backend — we don't want these exposed to the internet.
> - **LoadBalancer**: Azure provisions a public IP and forwards external traffic to the pods. Used for the Frontend Nginx — this is how users access the app.

### Q: What is a GitHub Actions "job" and "step"?
> A **job** is a set of steps that runs on the same virtual machine (runner). Jobs can run in parallel or in sequence (controlled by `needs:`). A **step** is a single task within a job — either an `action` (pre-built reusable script) or a `run` (custom shell commands).

### Q: What is `imagePullPolicy: Always` and why do we use it?
> It tells Kubernetes to always check Docker Hub for the latest version of the image before starting a pod, even if a local cached version exists. Without `Always`, Kubernetes might continue running old pods with stale code even after we push a new `:latest` tag.

### Q: What does `kubectl rollout restart` do?
> It forces all pods in a Deployment to be terminated and recreated one by one (rolling restart). This makes Kubernetes pull the freshest image (`:latest`) from Docker Hub and deploy it without any downtime — pods are replaced gradually, so some are always available.

### Q: How does Nginx know to forward `/api/` requests to the backend?
> The `nginx.conf` configuration file contains a `location /api/` block that uses `proxy_pass http://app:3000/api/`. Nginx acts as a reverse proxy — the browser talks only to Nginx (port 80), and Nginx internally forwards API requests to the backend. `app` is the Kubernetes ClusterIP Service name which the cluster DNS resolves automatically.

---

## ⚡ Quick Reference Commands Cheat Sheet

### Docker
```powershell
docker-compose up -d --build    # Start all services, rebuild images
docker-compose ps               # Check container status
docker-compose logs -f          # Live logs all containers
docker-compose logs -f app      # Live logs backend only
docker-compose down             # Stop containers
docker-compose down -v          # Stop + delete volumes
docker images                   # List local images
docker ps                       # List running containers
```

### Git
```powershell
git status                      # What's changed
git add .                       # Stage all changes
git commit -m "message"         # Commit
git push origin main            # Push (triggers CI/CD!)
git log --oneline               # Show commit history
```

### Kubernetes (kubectl)
```powershell
kubectl get pods                # List all pods and status
kubectl get svc                 # List services + external IPs
kubectl get pvc                 # List persistent volume claims
kubectl get nodes               # List cluster nodes
kubectl logs <pod-name>         # View pod logs
kubectl describe pod <pod>      # Detailed pod info (events, errors)
kubectl apply -f <file.yaml>    # Apply/update a manifest
kubectl delete -f <file.yaml>   # Delete resources from manifest
kubectl rollout restart deployment/<name>   # Force rolling restart
kubectl rollout status deployment/<name>    # Watch rollout progress
kubectl scale deployment/<name> --replicas=3  # Scale to 3 replicas
```

### Azure CLI
```powershell
az login                                       # Log in to Azure
az account show                                # Show active subscription
az aks get-credentials --resource-group devops-midterm-rg --name student-app-aks  # Connect kubectl
az group delete --name devops-midterm-rg --yes --no-wait  # ⚠️ CLEANUP (after viva!)
```

### Python Selenium Tests
```powershell
pip install -r selenium/requirements.txt                        # Install dependencies
python -m pytest selenium/tests/test_suite.py -v                # Run tests
python -m pytest selenium/tests/test_suite.py -v --html=report.html  # + HTML report
```

---

## 📚 Documentation Index

| File | Contents |
|---|---|
| [01-project-overview.md](./01-project-overview.md) | Architecture, project structure, tech stack, live URLs |
| [02-backend-and-frontend.md](./02-backend-and-frontend.md) | server.js, tasks.js, Dockerfiles, nginx.conf walkthrough |
| [03-docker-and-cicd.md](./03-docker-and-cicd.md) | docker-compose.yml, GitHub Actions pipeline (all 4 stages) |
| [04-kubernetes-manifests.md](./04-kubernetes-manifests.md) | PVC, Deployment, Service YAML files, AKS setup commands |
| [05-selenium-testing.md](./05-selenium-testing.md) | This file — test suite breakdown, Viva Q&A, cheat sheet |

---

*Quick-Task Hub — DevOps Final Exam Project | FA23-BCS-201 | COMSATS University Islamabad, Lahore Campus*

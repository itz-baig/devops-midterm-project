# Selenium Test Suite — Quick-Task Hub
## FA23-BCS-201 | DevOps Final Exam — Section D

## Overview
This directory contains **4 Selenium test cases** (TC-01 to TC-04) for the Quick-Task Hub application, implemented using Python + `pytest`.

| Test Case | Description |
|---|---|
| **TC-01** | Verify homepage loads with correct title, header, form, and stats |
| **TC-02** | Add a new task via the form and confirm it appears in the task list |
| **TC-03** | Filter tasks by status (High Priority, Pending, All) |
| **TC-04** | Validate frontend-to-backend API health endpoint (`/api/health`) |

---

## Prerequisites

- Python 3.8+
- Google Chrome installed
- App running locally (`docker-compose up -d`)

---

## Setup

```bash
# Navigate to the selenium directory
cd selenium

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate    # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

---

## Running Tests

```bash
# Run all tests with verbose output
pytest tests/test_suite.py -v

# Run with HTML report
pytest tests/test_suite.py -v --html=report.html --self-contained-html

# Run a specific test class
pytest tests/test_suite.py::TestAddTask -v

# Run against AKS deployment (change BASE_URL in test_suite.py)
# Edit BASE_URL = "http://<YOUR_AZURE_IP>"
pytest tests/test_suite.py -v
```

---

## Notes
- Tests use **headless Chrome** by default (no browser window opens)
- `webdriver-manager` automatically downloads the correct ChromeDriver version
- The `driver` fixture has **module scope** — one browser session for all tests (faster)
- TC-04 uses Python `requests` directly against the backend API (port 3000)

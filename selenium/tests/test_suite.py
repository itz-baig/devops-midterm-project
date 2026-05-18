"""
Quick-Task Hub — Selenium Test Suite
=====================================
Student : FA23-BCS-201
Project : Quick-Task Hub (DevOps Final Exam — Section D)

Test Cases:
  TC-01  Verify homepage loads with correct title
  TC-02  Add a new task via the form and confirm it appears in the list
  TC-03  Filter tasks by "High Priority" and verify filter applies
  TC-04  Validate frontend-to-backend API health endpoint response

Requirements:
  pip install -r requirements.txt

Run:
  pytest selenium/tests/test_suite.py -v --html=selenium/report.html
"""

import time
import requests
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

import os

# ── Configuration ─────────────────────────────────────────────────────────────
BASE_URL = "http://localhost:8080"   # Frontend (nginx) — change to Azure IP for AKS
API_URL  = "http://localhost:3000" # Backend direct (for API test)


# ── Fixtures ──────────────────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def driver():
    """Set up headless Chrome WebDriver using locally bundled chromedriver.exe."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,800")

    # Locate local chromedriver.exe relative to this test file
    local_driver = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "chromedriver.exe"))
    service = Service(executable_path=local_driver)
    
    drv = webdriver.Chrome(service=service, options=options)
    drv.implicitly_wait(10)

    yield drv

    drv.quit()


# ── TC-01: Homepage Loads ────────────────────────────────────────────────────
class TestHomepageLoads:
    """TC-01 — Verify the homepage loads with the correct title and key elements."""

    def test_page_title(self, driver):
        """The browser tab title must contain 'Quick-Task'."""
        driver.get(BASE_URL)
        time.sleep(2)
        assert "Quick-Task" in driver.title, (
            f"Expected 'Quick-Task' in title but got: '{driver.title}'"
        )
        print(f"\n✅ TC-01a PASS | Page title: {driver.title}")

    def test_header_visible(self, driver):
        """The 'Quick-Task Hub' heading must be visible in the header."""
        driver.get(BASE_URL)
        time.sleep(1)
        header = driver.find_element(By.TAG_NAME, "header")
        assert header.is_displayed(), "Header is not displayed"
        assert "Quick-Task Hub" in header.text, (
            f"Expected 'Quick-Task Hub' in header but got: '{header.text}'"
        )
        print("✅ TC-01b PASS | Header is visible with correct text")

    def test_add_task_form_present(self, driver):
        """The Add Task form must be present on the page."""
        driver.get(BASE_URL)
        form = driver.find_element(By.ID, "taskForm")
        assert form.is_displayed(), "Task form is not displayed"
        print("✅ TC-01c PASS | Add Task form is present")

    def test_stats_section_present(self, driver):
        """The 4 stats cards (Total, In Progress, Completed, High Priority) must exist."""
        driver.get(BASE_URL)
        stats = driver.find_elements(By.CLASS_NAME, "stat")
        assert len(stats) == 4, f"Expected 4 stat cards, found {len(stats)}"
        print(f"✅ TC-01d PASS | {len(stats)} stat cards found")


# ── TC-02: Add a New Task ─────────────────────────────────────────────────────
class TestAddTask:
    """TC-02 — Fill the form and submit a new task; verify it appears in the list."""

    TASK_TITLE = "Selenium Automated Test Task"

    def test_add_task_via_form(self, driver):
        """Submit the Add Task form and verify the new task appears in the list."""
        driver.get(BASE_URL)
        wait = WebDriverWait(driver, 15)

        # Fill in title
        title_input = wait.until(EC.presence_of_element_located((By.ID, "title")))
        title_input.clear()
        title_input.send_keys(self.TASK_TITLE)

        # Fill in description
        desc_input = driver.find_element(By.ID, "description")
        desc_input.send_keys("Created by Selenium TC-02 automated test")

        # Set priority to High
        priority_select = Select(driver.find_element(By.ID, "priority"))
        priority_select.select_by_value("high")

        # Set status to In Progress
        status_select = Select(driver.find_element(By.ID, "status"))
        status_select.select_by_value("in-progress")

        # Submit
        add_btn = driver.find_element(By.ID, "addBtn")
        add_btn.click()

        # Wait for task to appear in list
        time.sleep(2)
        task_list = driver.find_element(By.ID, "taskList")
        assert self.TASK_TITLE in task_list.text, (
            f"Expected '{self.TASK_TITLE}' in task list but got:\n{task_list.text}"
        )
        print(f"✅ TC-02 PASS | Task '{self.TASK_TITLE}' created and visible in list")

    def test_stats_update_after_add(self, driver):
        """Total task count stat should be at least 1 after adding a task."""
        driver.get(BASE_URL)
        time.sleep(2)
        total_stat = driver.find_element(By.ID, "statTotal")
        count = int(total_stat.text)
        assert count >= 1, f"Expected total tasks >= 1 but got: {count}"
        print(f"✅ TC-02b PASS | Total tasks stat shows: {count}")


# ── TC-03: Filter Tasks ───────────────────────────────────────────────────────
class TestFilterTasks:
    """TC-03 — Click the 'High Priority' filter and verify it becomes active."""

    def test_high_priority_filter(self, driver):
        """Clicking 'High Priority' filter button should set it as active."""
        driver.get(BASE_URL)
        wait = WebDriverWait(driver, 10)

        # Find the High Priority filter button
        filter_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-filter='high']"))
        )
        filter_btn.click()
        time.sleep(1)

        # Verify it has 'active' class
        btn_classes = filter_btn.get_attribute("class")
        assert "active" in btn_classes, (
            f"Expected filter button to be active but classes are: '{btn_classes}'"
        )
        print("✅ TC-03a PASS | High Priority filter button is active")

    def test_all_filter_resets(self, driver):
        """Clicking 'All' filter after 'High Priority' should reset to All."""
        driver.get(BASE_URL)
        wait = WebDriverWait(driver, 10)

        # Click High Priority first
        hp_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-filter='high']"))
        )
        hp_btn.click()
        time.sleep(0.5)

        # Click All
        all_btn = driver.find_element(By.XPATH, "//button[@data-filter='all']")
        all_btn.click()
        time.sleep(0.5)

        all_classes = all_btn.get_attribute("class")
        assert "active" in all_classes, (
            f"Expected 'All' filter to be active but classes are: '{all_classes}'"
        )
        print("✅ TC-03b PASS | 'All' filter is active after reset")

    def test_pending_filter(self, driver):
        """Clicking 'Pending' filter button should set it as active."""
        driver.get(BASE_URL)
        wait = WebDriverWait(driver, 10)

        pending_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-filter='pending']"))
        )
        pending_btn.click()
        time.sleep(1)

        btn_classes = pending_btn.get_attribute("class")
        assert "active" in btn_classes, (
            f"Expected Pending filter to be active but classes are: '{btn_classes}'"
        )
        print("✅ TC-03c PASS | Pending filter button is active")


# ── TC-04: API Health Check ───────────────────────────────────────────────────
class TestAPIHealthCheck:
    """TC-04 — Validate the backend /api/health endpoint returns expected JSON."""

    def test_health_endpoint_status_code(self):
        """GET /api/health must return HTTP 200."""
        response = requests.get(f"{API_URL}/api/health", timeout=10)
        assert response.status_code == 200, (
            f"Expected status 200 but got: {response.status_code}"
        )
        print(f"✅ TC-04a PASS | /api/health returned HTTP {response.status_code}")

    def test_health_endpoint_json_structure(self):
        """Response JSON must contain 'status' key with value 'ok'."""
        response = requests.get(f"{API_URL}/api/health", timeout=10)
        data = response.json()
        assert "status" in data, f"'status' key missing from response: {data}"
        assert data["status"] == "ok", (
            f"Expected status='ok' but got: '{data.get('status')}'"
        )
        print(f"✅ TC-04b PASS | /api/health JSON: {data}")

    def test_health_endpoint_db_status(self):
        """Response must contain 'db' field indicating database connectivity."""
        response = requests.get(f"{API_URL}/api/health", timeout=10)
        data = response.json()
        assert "db" in data, f"'db' key missing from response: {data}"
        assert data["db"] in ("connected", "disconnected"), (
            f"Unexpected 'db' value: '{data.get('db')}'"
        )
        print(f"✅ TC-04c PASS | DB status: {data.get('db')}")

    def test_tasks_api_endpoint(self):
        """GET /api/tasks must return HTTP 200 with a JSON array."""
        response = requests.get(f"{API_URL}/api/tasks", timeout=10)
        assert response.status_code == 200, (
            f"Expected status 200 but got: {response.status_code}"
        )
        data = response.json()
        assert isinstance(data, list), (
            f"Expected a JSON array but got: {type(data).__name__}"
        )
        print(f"✅ TC-04d PASS | /api/tasks returned {len(data)} tasks")

    def test_db_indicator_on_page(self, driver):
        """The DB connection pill on the page must show 'MongoDB Connected'."""
        driver.get(BASE_URL)
        time.sleep(3)
        db_label = driver.find_element(By.ID, "dbLabel")
        label_text = db_label.text
        assert "Connected" in label_text or "Disconnected" in label_text, (
            f"Unexpected DB label text: '{label_text}'"
        )
        print(f"✅ TC-04e PASS | DB indicator shows: '{label_text}'")

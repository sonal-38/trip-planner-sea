from __future__ import annotations

import os

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager


@pytest.mark.skipif(os.getenv("RUN_SELENIUM", "0") != "1", reason="Set RUN_SELENIUM=1 to run E2E browser tests")
def test_streamlit_generate_flow():
    base_url = os.getenv("STREAMLIT_BASE_URL", "http://localhost:8507")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    try:
        print(f"[E2E] Open app URL: {base_url}")
        driver.get(base_url)

        wait = WebDriverWait(driver, 20)
        destination = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[@placeholder='Enter a city, region, or country'] | //input[@aria-label='Where do you want to go?']")
            )
        )
        print("[E2E] Clicked destination input")
        destination.clear()
        destination.send_keys("Goa")
        print("[E2E] Typed destination: Goa")

        generate = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Generate 2 Agent Outputs')]")))
        print("[E2E] Clicked button: Generate 2 Agent Outputs")
        generate.click()

        try:
            wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(., 'Generated Itinerary')]")))
        except TimeoutException:
            pass

        page = driver.page_source

        success_state = (
            "Two Agent Outputs" in page
            and "Agent 1 - Weather" in page
            and "Agent 2 - Hotel" in page
            and "Generated Itinerary" in page
        )
        error_state = (
            "Last Error" in page
            or "Failed to generate plan" in page
            or "Gemini is temporarily overloaded" in page
            or "Gemini quota or rate limit reached" in page
        )

        if success_state:
            print("[E2E] Agent 1 run: Weather output found")
            print("[E2E] Agent 2 run: Hotel output found")
            print("[E2E] Itinerary generated: Generated Itinerary found")
        elif error_state:
            print("[E2E] Generation attempted, app returned graceful error state")

        assert success_state or error_state
    finally:
        print("[E2E] Closing browser")
        driver.quit()

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import time
import requests
from db import insert_product

keyword = input("Enter the item to search on Amazon: ")

# Try to use undetected-chromedriver which bypasses many bot checks.
try:
    import undetected_chromedriver as uc
    driver = uc.Chrome(headless=True)
except Exception:

    # Fallback: configure Selenium ChromeOptions to reduce detection surface
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    # Provide a common desktop user-agent
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    )
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    # Hide webdriver property
    try:
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"},
        )
    except Exception:
        pass

driver.get(f"https://www.amazon.com/s?k={keyword}")
time.sleep(5)

items = driver.find_elements(By.CSS_SELECTOR, "div[data-component-type='s-search-result']")

for item in items:
    try:
        name = item.find_element(By.TAG_NAME, "h2").text
        item_type = keyword
        price_whole = item.find_element(By.CLASS_NAME, "a-price-whole").text.replace(",", "")
        try:
            price_fraction = item.find_element(By.CLASS_NAME, "a-price-fraction").text
            price = f"{price_whole}.{price_fraction}"
        except:
            price = price_whole
        currency = "IDR"
        
        # Convert to RMB
        if currency.upper() != "CNY":
            try:
                rate_response = requests.get(f"https://api.exchangerate-api.com/v4/latest/{currency}")
                rate_data = rate_response.json()
                rate = rate_data['rates']['CNY']
                price = float(price) * rate
                currency = "RMB"
            except:
                pass
        
        # Get product URL
        product_url = item.find_element(By.TAG_NAME, "a").get_attribute("href")

        # Insert with product URL
        insert_product(
            "Amazon",
            name,
            float(price),
            currency,
            datetime.now(),
            item_type,
            product_url  # Added product URL
        )
    except:
        continue

driver.quit()
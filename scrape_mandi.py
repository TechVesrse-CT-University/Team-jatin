from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import pandas as pd

options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

driver.get("https://agmarknet.gov.in/SearchCmmMkt.aspx")
time.sleep(3)

state_dropdown = driver.find_element(By.ID, "cphBody_ddlState")
states = [option.text for option in state_dropdown.find_elements(By.TAG_NAME, "option")]

# 💡 Simulate scraped mandi price data
data = {
    "state": ["Maharashtra", "Punjab"],
    "market": ["Pune", "Ludhiana"],
    "crop": ["Tomato", "Wheat"],
    "modal_price": [2200, 2000],
    "unit": ["Rs/Quintal", "Rs/Quintal"],
    "date": [time.strftime('%Y-%m-%d')] * 2
}
df = pd.DataFrame(data)
df.to_csv("mandi_data.csv", index=False)
print("✅ Mandi data saved!")

driver.quit()

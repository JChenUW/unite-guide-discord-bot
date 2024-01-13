#Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as expectedCond
from selenium.common.exceptions import TimeoutException
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor
import pandas as pd

def scrape_tier_list():
    options=ChromeOptions()
    options.add_argument("--headless")
    #options.add_experimental_option("detach", True) #keeps window open
    chromedriver_path=\
        "C:\\Users\\Jc050\\OneDrive\\Documents\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe" #path for executable
    service=Service(executable_path=chromedriver_path)

    #opens browser window
    browser=webdriver.Chrome(service=service, options=options)
    url="https://unite-db.com/tier-list/pokemon" #url of site to be scraped
    browser.get(url)

    #extract tier list info using xpath
    tiers=browser.find_elements(By.XPATH, "//*[@class='tier']")
    tier_names=browser.find_elements(By.XPATH, "//*[@class='ranking-title']")
    tier_list={}
    for i in range(0,len(tiers)):
        mons=[]
        tier_content=tiers[i].find_elements(By.XPATH, ".//div//p")
        for j in tier_content:
            mons.append(j.text.lower())
        tier_list[tier_names[i].text]=mons


    print(tier_list)


    #Extract data to .csv
    data=pd.DataFrame.from_dict(tier_list, orient = 'index')
    path="C:\\Users\\Jc050\\OneDrive\\Documents\\Unite Guide Discord Bot\\pythonProject1\\Data\\tier_list.csv"
    data.to_csv(path,mode="w+")
    browser.quit()


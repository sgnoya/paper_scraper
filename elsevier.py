# %%
import os
import time

import requests
from bs4 import BeautifulSoup
from omegaconf import OmegaConf
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from utils import discord, init_twitterapi

options = Options()
options.add_argument("--headless")
options.add_argument('window-size=1400,600')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--user-agent=Chrome/110")
options.add_experimental_option('prefs', {
    'credentials_enable_service': False,
    'profile': {'password_manager_enabled': False}
})

cwd, _ = os.path.split(os.path.abspath(__file__))
keys = OmegaConf.load(os.path.join(cwd, "keys.yml"))
subscribe = OmegaConf.load(os.path.join(cwd, "subscribe.yml"))

journals = subscribe.elsevier.journals

twkeys = keys.twitter.app
twapi = init_twitterapi(
    twkeys.apikey, twkeys.apisecret, twkeys.token, twkeys.tokensecret
)

with open(os.path.join(cwd, "elsevier.csv"), "r") as f:
    data = f.readlines()

sent = []

# %%
driver = webdriver.Chrome(options=options)
driver.implicitly_wait(5)

# %%
for journal in journals:
    url = "https://www.sciencedirect.com/journal/" + journal + "/articles-in-press"
    print(url)
    driver.get(url)
    time.sleep(5)
    elem = driver.find_elements(By.CSS_SELECTOR, ".text-m.u-font-serif.u-display-inline")
    papers = []
    for e in elem:
        soup = BeautifulSoup(e.get_attribute("innerHTML"), "html.parser")
        title = e.find_element(By.CLASS_NAME, "js-article-title").text.replace("\n", " ")
        papers.append([title, "https://www.sciencedirect.com"+ soup.find("a").get("href")])

    msg = "@here (Elsevier)" + journal + "\n"
    discord(keys.discord, msg)

    msg = ""
    for i, (title, link) in enumerate(papers):
        if title + "\n" not in data:
            msg += title + "\n" + link + "\n"
            sent.append(title + "\n")

            _msg = "[Elsevier: " + journal + "]\n"
            _msg += title + "\n" + link + "\n"
            try:
                twapi.update_status(_msg)
            except Exception as e:
                print(e)
                print(journal, title, link)



with open(os.path.join(cwd, "elsevier.csv"), "a") as f:
    f.writelines(sent)

driver.quit()
